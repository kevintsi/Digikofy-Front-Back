from abc import ABC
from ..modules.response_models import CreatePreparation, MachineUpdate, PreparationSaved, UpdatePreparationSaved,\
    UserAuthentication, MachineCreate, Machine, Coffee, Preparation, UserRefreshToken
from firebase_admin import auth
from ..firebase import db
from datetime import datetime, timedelta
from os import getenv
import requests
import pytz


class UserService(ABC):
    def create_user(self, data: UserAuthentication):
        try:
            new_user = auth.create_user(
                email=data.email,
                password=data.password
            )
            
            doc_ref = db.collection('users').document(
                new_user.uid)
            doc_ref.set({
                'uid': new_user.uid,
                'email': new_user.email
            })
            return 201
        except auth.EmailAlreadyExistsError as ex:
            print(type(ex))
            return 409
        except Exception as ex:
            return 500

    def log_in_user(self, data: UserAuthentication):

        response = requests.post(
            url="https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword",
            params={"key": getenv("API_KEY_FIREBASE")},
            data=data.json()
        )

        print(f"Response : {response}, code : {response.status_code}")

        if response.status_code == 200:
            return response.json()
        else:
            return None

    def delete_user(self, user_id: str):
        auth.delete_user(user_id)
        db.collection("users").document(user_id).delete()
        docs_machine = db.collection("machines").stream()
        for doc in docs_machine:
            user_exist = db.collection("machines").document(
                doc.id).collection("users").document(user_id).get().exists
            if user_exist:
                db.collection("machines").document(doc.id).collection(
                    "users").document(user_id).delete()

        return 200

    def get_new_token(self, data: UserRefreshToken):

        docs = db.collection("refreshTokensBlackList").where(
            "refresh_token", "==", data.refresh_token).get()

        if len(docs) > 0:
            return None, 403
        else:
            response = requests.post(
                url="https://securetoken.googleapis.com/v1/token",
                params={"key": getenv("API_KEY_FIREBASE")},
                data={"grant_type": "refresh_token",
                      "refresh_token": data.refresh_token}
            )

            print(f"Response : {response}, code : {response.status_code}")

            if response.status_code == 200:
                return response.json(), response.status_code
            else:
                return None, response.status_code

    def revoke_refresh_token(self, data: UserRefreshToken):
        db.collection("refreshTokensBlackList").add(data.dict())


class MachineService(ABC):

    def create_machine(self, data: MachineCreate, id_user: str):
        """
        Create machine

        Args:
            data (MachineCreate): [Data model for creating MachineCreate]

        Returns:
            [Code]: [Status code]
        """
        try:
            print("----- Start create_machine ----")
            users_exist = db.collection('machines').document(
                data.id).collection("users").get()
            print(len(users_exist))
            if len(users_exist) == 0:
                print("Machine never created so no users => creating...")

                db.collection("machines").document(data.id).set({
                    "id": data.id,
                    "state": data.state,
                    "type": data.type
                })

                db.collection("machines").document(data.id).collection("users").document(id_user).set({
                    "name": data.name,
                    "uid": id_user,
                    "last_update" : datetime.now(tz=pytz.utc),
                    "creation_date" : datetime.now(tz=pytz.utc)
                })

            else:
                print("Machine already created so users => adding user...")
                db.collection("machines").document(data.id).collection("users").document(id_user).set({
                    "name": data.name,
                    "uid": id_user,
                    "last_update" : datetime.now(tz=pytz.utc),
                    "creation_date" : datetime.now(tz=pytz.utc)
                })
            print("----- End create_machine ----")
            return 201
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500

    def get_machines(self, id_user: str):
        """

        Get all the machines available

        Returns:
            [list(Machine)]: [List of machines]
        """
        try:

            print("------ Start get machines ------")
            machines = []
            doc_machines = db.collection('machines').stream()
            for doc in doc_machines:
                dico_machine = doc.to_dict()
                print(dico_machine)
                docs_user_machine = db.collection('machines').document(dico_machine["id"]).collection(
                    "users").where("uid", "==", id_user).stream()
                print("Get machines ---> {}".format(docs_user_machine))
                for doc_mach_user in docs_user_machine:
                    dico_machine_user = doc_mach_user.to_dict()
                    print("User's machine info : {}".format(dico_machine_user))
                    machines.append(Machine(
                        id=dico_machine["id"], 
                        name=dico_machine_user["name"], 
                        state=dico_machine["state"], type=dico_machine["type"], 
                        last_update=convert_to_datetime(dico_machine_user["last_update"]), 
                        creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                        ))
            print(machines)
            print("------ End get machines ------")
            return 200, machines
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500, []

    def get_machine_by_id(self, id: str, id_user: str):
        """

        Get machine by a given id

        Args:
            id (str): [Machine's id]

        Returns:
            [Machine]: [Machine found]
        """
        try:
            print("------ Start get machine by id ------")
            machine = None
            doc_machine = db.collection('machines').document(id).get()
            if doc_machine.exists:
                doc_machine = doc_machine.to_dict()
                print(doc_machine)
                doc_machine_user = db.collection("machines").document(id).collection(
                    "users").document(id_user).get()
                print(doc_machine_user)
                dico_machine_user = doc_machine_user.to_dict()
                print(dico_machine_user)
                print("User's machine info : {}".format(dico_machine_user))
                machine = Machine(
                    id=doc_machine["id"], 
                    name=dico_machine_user["name"],
                    state=doc_machine["state"], 
                    type=doc_machine["type"],
                    last_update=convert_to_datetime(dico_machine_user["last_update"]),
                    creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                    )
                print(machine)
            else:
                return 404, machine
            print("------ End get machines ------")
            return 200, machine
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500, machine

    def update_machine(self, id: str, data: MachineUpdate, id_user: str):
        """

        Update machine

        Args:
            id (str): [Id of machine]
            data (MachineUpdate): [data use for updates]

        Returns:
            [Code]: [Status code]
        """
        try:
            print("----- Start update machine's name -----")
            print("{}".format(id))
            db.collection("machines").document(id).collection("users").document(
                id_user).update({"name": data.name, "last_update" : datetime.now(tz=pytz.utc)})
            print("------ End update machine's name -----")
            return 200
        except Exception as ex:
            print("Error : {}".format(ex))
            return 404

    def delete_machine(self, id: str, id_user: str):
        """

        Delete the machine with the given id

        Args:
            id (str): [Machine's id]

        Returns:
            [Code]: [Status code]
        """
        try:
            print("----- Start delete_machine -----")
            document = db.collection("machines").document(id)
            if document.get().exists:

                if len(document.collection("users").get()) == 0:

                    document.delete()

                    users = db.collection("users").stream()

                    for user in users:

                        preps = db.collection("users").document(
                            user.id).collection("preparations").stream()

                        for prep in preps:

                            prep_dict = prep.to_dict()

                            if prep_dict["machine"].id == id:
                                prep.reference.delete()

                else:

                    if document.collection("users").document(id_user).get().exists:

                        document.collection("users").document(id_user).delete()

                        preps = db.collection("users").document(
                            id_user).collection("preparations").stream()

                        for prep in preps:

                            prep_dict = prep.to_dict()

                            if prep_dict["machine"].id == id:
                                prep.reference.delete()

                print("------ End delete_machine -----")
                return 200
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500


class PreparationService(ABC):
    def get_preparation_machine(self, id: str):
        """
        Return all preparations that are programmed for a future time with machine with the given id

        Args:
            id (str): [Id of machine]

        Returns:
            [list]: [Preparations]
        """
        list_preparations = list()
        try:
            print("------ Start get_preparation_machine ------")
            machine_ref = db.collection("machines").document(id)
            print(machine_ref)

            if machine_ref.get().exists:

                users = db.collection("users").stream()

                for user in users:
                    preparations = db.collection("users").document(
                        user.id).collection("preparations").stream()
                    print(
                        "Docs preparation with id : {} ---> {}".format(id, preparations))

                    for preparation in preparations:

                        prepa_dict = preparation.to_dict()
                        nextTime = prepa_dict["nextTime"]
                        year, month, day, hour, minute, second = nextTime.year, nextTime.month, nextTime.day, nextTime.hour, nextTime.minute, nextTime.second

                        date_preparation = datetime(
                            year, month, day, hour, minute, second)
                        print("Early : {}".format(not date_preparation <
                                                  datetime.now() and prepa_dict["state"] == 0))
                        if not date_preparation < datetime.now() and prepa_dict["state"] == 0:

                            print("Preparation not yet passed")

                            doc_coffee = db.collection("coffees").document(
                                prepa_dict["coffee"].id).get()

                            doc_coffee = doc_coffee.to_dict()

                            coffee = Coffee(id=doc_coffee["id"], name=doc_coffee["name"],
                                            description=doc_coffee["description"])

                            doc_machine = db.collection("machines").document(
                                prepa_dict["machine"].id).get()

                            dico_machine_user = db.collection("machines").document(prepa_dict["machine"].id).collection(
                                "users").document(user.id).get().to_dict()

                            doc_machine = doc_machine.to_dict()

                            machine = Machine(
                                id=doc_machine["id"], 
                                state=doc_machine["state"],
                                type=doc_machine["type"], 
                                name=dico_machine_user["name"],
                                last_update=convert_to_datetime(dico_machine_user["last_update"]),
                                creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                                )

                            if prepa_dict["saved"]:
                                print("Preparation saved")
                                prep = PreparationSaved(coffee=coffee, creation_date=convert_to_datetime(prepa_dict["creationDate"]), last_update=convert_to_datetime(prepa_dict["lastUpdate"]), machine=machine,
                                                        id=prepa_dict["id"], saved=prepa_dict["saved"], state=prepa_dict[
                                                            "state"], next_time=convert_to_datetime(prepa_dict["nextTime"]),
                                                        days_of_week=prepa_dict["daysOfWeek"], hours=prepa_dict["hours"], last_time=convert_to_datetime(prepa_dict["lastTime"]), name=prepa_dict["name"])
                                print("Preparation : {}".format(prep))
                            else:
                                print("Preparation not saved")
                                prep = Preparation(coffee=coffee, creation_date=convert_to_datetime(prepa_dict["creationDate"]), last_update=convert_to_datetime(prepa_dict["lastUpdate"]), machine=machine,
                                                   id=prepa_dict["id"], saved=prepa_dict["saved"], state=prepa_dict["state"], next_time=convert_to_datetime(prepa_dict["nextTime"]))

                            print("Preparation : {}".format(prep))
                            list_preparations.append(prep)

                print("------ End get_preparation_machine ------")
                return 200, list_preparations
            else:
                return 404, list_preparations
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500, list_preparations

    def get_preparation_next_coffee(self, id: str):
        """
        Return all preparations that already passed with machine with the given id

        Args:
            id (str): [Id of machine]

        Returns:
            [list]: [Preparations]
        """
        list_preparations = list()
        try:
            print("------ Start get_preparation_machine ------\n")
            machine_ref = db.collection("machines").document(id)
            print(machine_ref)

            if machine_ref.get().exists:

                users = db.collection("users").stream()

                for user in users:
                    preparations = db.collection("users").document(
                        user.id).collection("preparations").stream()
                    print(
                        "Docs preparation with id : {} ---> {}\n".format(id, preparations))

                    for preparation in preparations:

                        prepa_dict = preparation.to_dict()
                        nextTime = prepa_dict["nextTime"]
                        year, month, day, hour, minute, second = nextTime.year, nextTime.month, nextTime.day, nextTime.hour, nextTime.minute, nextTime.second

                        date_preparation = datetime(
                            year, month, day, hour, minute, second)

                        print("Early : {}".format(date_preparation <
                                                  datetime.now() and prepa_dict["state"] == 0))

                        if date_preparation < datetime.now() and prepa_dict["state"] == 0:

                            print("Preparation passed\n")

                            doc_coffee = db.collection("coffees").document(
                                prepa_dict["coffee"].id).get()

                            doc_coffee = doc_coffee.to_dict()

                            coffee = Coffee(id=doc_coffee["id"], name=doc_coffee["name"],
                                            description=doc_coffee["description"])

                            doc_machine = db.collection("machines").document(
                                prepa_dict["machine"].id).get()

                            dico_machine_user = db.collection("machines").document(prepa_dict["machine"].id).collection(
                                "users").document(user.id).get().to_dict()

                            doc_machine = doc_machine.to_dict()

                            machine = Machine(
                                id=doc_machine["id"], 
                                state=doc_machine["state"],
                                type=doc_machine["type"], 
                                name=dico_machine_user["name"],
                                last_update=convert_to_datetime(dico_machine_user["last_update"]),
                                creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                                )

                            if prepa_dict["saved"]:
                                print("Preparation saved\n")
                                prep = PreparationSaved(coffee=coffee, creation_date=convert_to_datetime(prepa_dict["creationDate"]), last_update=convert_to_datetime(prepa_dict["lastUpdate"]), machine=machine,
                                                        id=prepa_dict["id"], saved=prepa_dict["saved"], state=prepa_dict[
                                                            "state"], next_time=convert_to_datetime(prepa_dict["nextTime"]),
                                                        days_of_week=prepa_dict["daysOfWeek"], hours=prepa_dict["hours"], last_time=convert_to_datetime(prepa_dict["lastTime"]), name=prepa_dict["name"])
                                print("Preparation : {}\n".format(prep))
                            else:
                                print("Preparation not saved\n")
                                prep = Preparation(coffee=coffee, creation_date=convert_to_datetime(prepa_dict["creationDate"]), last_update=convert_to_datetime(prepa_dict["lastUpdate"]), machine=machine,
                                                   id=prepa_dict["id"], saved=prepa_dict["saved"], state=prepa_dict["state"], next_time=convert_to_datetime(prepa_dict["nextTime"]))

                            print("Preparation : {}\n".format(
                                list_preparations))

                            list_preparations.append(prep)

                list_preparations.sort(
                    key=lambda x: x.next_time, reverse=False)

                print("Preparations sorted : {}\n".format(list_preparations))

                print("------ End get_preparation_machine ------")
                return 200, list_preparations
            else:
                return 404, list_preparations
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500, list_preparations

    def get_preparation(self, id_user: str):
        preparations = list()
        try:
            print("------ Start get preparation ------")
            docs = db.collection("users").document(
                id_user).collection("preparations").stream()
            print("Get Preparation ---> {}".format(docs))
            for doc in docs:
                dico = doc.to_dict()
                print("Coffee reference id --> {}".format(dico["coffee"].id))
                doc_coffee = db.collection("coffees").document(
                    dico["coffee"].id).get()
                coffee = doc_coffee.to_dict()
                print("Information coffee --> {}".format(coffee))
                print(Coffee(id=coffee["id"], name=coffee["name"],
                      description=coffee["description"]))

                coffee = Coffee(id=coffee["id"], name=coffee["name"],
                                description=coffee["description"])

                print("Machine reference id --> {}".format(dico["machine"].id))
                doc_machine = db.collection("machines").document(
                    dico["machine"].id).get()
                machine = doc_machine.to_dict()
                print("Information machine --> {}".format(machine))

                dico_machine_user = db.collection("machines").document(dico["machine"].id).collection(
                    "users").document(id_user).get().to_dict()

                machine = Machine(
                    id=machine["id"], 
                    state=machine["state"],
                    type=machine["type"], 
                    name=dico_machine_user["name"],
                    last_update=convert_to_datetime(dico_machine_user["last_update"]),
                    creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                    )

                print(dico)
                if dico["saved"]:
                    print("Preparation saved")
                    preparation = PreparationSaved(coffee=coffee, creation_date=convert_to_datetime(dico["creationDate"]), last_update=convert_to_datetime(dico["lastUpdate"]), machine=machine,
                                                   id=dico["id"], saved=dico["saved"], state=dico["state"], next_time=convert_to_datetime(dico["nextTime"]), name=dico["name"], days_of_week=dico["daysOfWeek"], hours=dico["hours"], last_time=convert_to_datetime(dico["lastTime"]))
                else:
                    print("Preparation not saved")
                    preparation = Preparation(coffee=coffee, creation_date=convert_to_datetime(dico["creationDate"]), last_update=convert_to_datetime(dico["lastUpdate"]), machine=machine,
                                              id=dico["id"], saved=dico["saved"], state=dico["state"], next_time=convert_to_datetime(dico["nextTime"]))
                preparations.append(preparation)
            print("{}".format(preparations))
            print("------ End get preparation  ------")
            return 200, preparations
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500, preparations

        
    def get_next_preparation(self, id_user : str):
        try:
            preps = db.collection("users").document(id_user).collection("preparations").get()
            if len(preps) == 0:
                return 200, None
            next_prep = preps[0]
            for prep in preps:
                #print(f"Start with {prep.to_dict()['nextTime']}")
                prep_dict = prep.to_dict()
                #print(f"Superior to old next_prep : {prep_dict['nextTime'] < next_prep.to_dict()['nextTime']}")
                #print(f"Date superior to current date : {prep_dict['nextTime'] > datetime.now(tz=pytz.UTC)}\n\n\n")

                if (prep_dict["nextTime"] < next_prep.to_dict()["nextTime"]) and (prep_dict["nextTime"] > datetime.now(tz=pytz.utc)):
                    #print(f'New next_prep : {prep.to_dict()["nextTime"]}\n\n')
                    next_prep = prep
                    print(f"New next_prep : {next_prep.to_dict()['nextTime']}")

            if next_prep == None:
                return 200, None

            print(f"Next preparation : {next_prep.to_dict()}")
            dico = next_prep.to_dict()
            doc_coffee = db.collection("coffees").document(
            dico["coffee"].id).get()
            coffee = doc_coffee.to_dict()
            #print("Information coffee --> {}".format(coffee))
            #print(Coffee(id=coffee["id"], name=coffee["name"],description=coffee["description"]))

            coffee = Coffee(id=coffee["id"], name=coffee["name"],
                            description=coffee["description"])

            #print("Machine reference id --> {}".format(dico["machine"].id))
            doc_machine = db.collection("machines").document(
                dico["machine"].id).get()
            machine = doc_machine.to_dict()
            #print("Information machine --> {}".format(machine))

            dico_machine_user = db.collection("machines").document(dico["machine"].id).collection(
                "users").document(id_user).get().to_dict()

            #print(Machine(id=machine["id"], state=machine["state"],type=machine["type"], name=user["name"]))

            machine = Machine(
                id=machine["id"], 
                state=machine["state"],
                type=machine["type"], 
                name=dico_machine_user["name"],
                last_update=convert_to_datetime(dico_machine_user["last_update"]),
                creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                )

            if next_prep.to_dict()["saved"]:
                return 200, PreparationSaved(coffee=coffee, creation_date=convert_to_datetime(dico["creationDate"]), last_update=convert_to_datetime(dico["lastUpdate"]), machine=machine,
                                                   id=dico["id"], saved=dico["saved"], state=dico["state"], next_time=convert_to_datetime(dico["nextTime"]), name=dico["name"], days_of_week=dico["daysOfWeek"], hours=dico["hours"], last_time=convert_to_datetime(dico["lastTime"]))
            else:
                return 200, Preparation(coffee=coffee, creation_date=convert_to_datetime(dico["creationDate"]), last_update=convert_to_datetime(dico["lastUpdate"]), machine=machine,
                                              id=dico["id"], saved=dico["saved"], state=dico["state"], next_time=convert_to_datetime(dico["nextTime"]))
        except Exception as ex:
            print(f"Error : {ex}")
            return 500, None

    def get_last_preparation(self, id_user : str):
        try:
            preps = db.collection("users").document(id_user).collection("preparations").get()
            if len(preps) == 0:
                return 200, None
            last_prep = preps[0]
            for prep in preps:
                #print(f"Start with {prep.to_dict()['nextTime']}")
                prep_dict = prep.to_dict()
                #print(f"Superior to old next_prep : {prep_dict['nextTime'] < next_prep.to_dict()['nextTime']}")
                #print(f"Date superior to current date : {prep_dict['nextTime'] > datetime.now(tz=pytz.UTC)}\n\n\n")
                if prep_dict["saved"]:
                    if (prep_dict["lastTime"] > last_prep.to_dict()["lastTime"]) and (prep_dict["lastTime"] < datetime.now(tz=pytz.utc)):
                        #print(f'New next_prep : {prep.to_dict()["nextTime"]}\n\n')
                        last_prep = prep
                        print(f"New last_prep : {last_prep.to_dict()['nextTime']}")
            
            if last_prep == None or not last_prep.to_dict()["saved"]:
                return 200,None

            print(f"Last preparation : {last_prep.to_dict()}")
            dico = last_prep.to_dict()
            doc_coffee = db.collection("coffees").document(
            dico["coffee"].id).get()
            coffee = doc_coffee.to_dict()
            #print("Information coffee --> {}".format(coffee))
            #print(Coffee(id=coffee["id"], name=coffee["name"],description=coffee["description"]))

            coffee = Coffee(id=coffee["id"], name=coffee["name"],
                            description=coffee["description"])

            #print("Machine reference id --> {}".format(dico["machine"].id))
            doc_machine = db.collection("machines").document(
                dico["machine"].id).get()
            machine = doc_machine.to_dict()
            #print("Information machine --> {}".format(machine))

            dico_machine_user = db.collection("machines").document(dico["machine"].id).collection(
                "users").document(id_user).get().to_dict()

            #print(Machine(id=machine["id"], state=machine["state"],type=machine["type"], name=user["name"]))

            machine = Machine(
                id=machine["id"], 
                state=machine["state"],
                type=machine["type"], 
                name=dico_machine_user["name"],
                last_update=convert_to_datetime(dico_machine_user["last_update"]),
                creation_date=convert_to_datetime(dico_machine_user["creation_date"])
                )

            return 200, PreparationSaved(coffee=coffee, creation_date=convert_to_datetime(dico["creationDate"]), last_update=convert_to_datetime(dico["lastUpdate"]), machine=machine,
                                                id=dico["id"], saved=dico["saved"], state=dico["state"], next_time=convert_to_datetime(dico["nextTime"]), name=dico["name"], days_of_week=dico["daysOfWeek"], hours=dico["hours"], last_time=convert_to_datetime(dico["lastTime"]))
        except Exception as ex:
            print(f"Error : {ex}")
            return 500, None

    def report_preparation_started(self, id: str, id_user: str):
        try:
            print("------ Start report_preparation_started ------")

            user = db.collection("users").document(id_user)

            prep = user.collection("preparations").document(id)

            if prep.get().exists:

                print(prep)
                prep.update({"state": 1})

                machine_id = prep.get().to_dict()["machine"].id
                print(machine_id)

                db.collection("machines").document(
                    machine_id).update({"state": 1})

                notif_ref = user.collection("notifications").document()

                notif_ref.set({
                    "id": notif_ref.id,
                    "preparation": prep,
                    "state": 0
                })

                print("------ End report_preparation_started ------")

                return 200
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500

    def report_preparation_succeeded(self, id: str, id_user: str):
        try:
            print("------ Start report_preparation_succeeded ------")

            user = db.collection("users").document(id_user)

            prep = user.collection("preparations").document(id)

            if prep.get().exists:

                print(prep)
                prep.update({"state": 1})

                machine_id = prep.get().to_dict()["machine"].id
                print(machine_id)

                db.collection("machines").document(
                    machine_id).update({"state": 0})

                prep_dict = prep.get().to_dict()

                is_saved = prep_dict["saved"]

                if is_saved:

                    next_time = calculate_next_time(
                        prep_dict["daysOfWeek"], prep_dict["hours"])

                    print("New value of next_time = {}".format(next_time))

                    prep.update({
                        "lastTime": prep_dict["nextTime"],
                        "nextTime": next_time
                    })

                notif_ref = user.collection("notifications").document()

                notif_ref.set({
                    "id": notif_ref.id,
                    "preparation": prep,
                    "state": 1
                })

                print("------ End report_preparation_succeeded ------")

                return 200
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500

    def report_preparation_failed(self, id: str, id_user: str):
        try:
            print("------ Start report_preparation_failed ------")

            user = db.collection("users").document(id_user)

            prep = user.collection("preparations").document(id)

            if prep.get().exists:

                print(prep)
                prep.update({"state": 0})

                machine_id = prep.get().to_dict()["machine"].id
                print(machine_id)

                db.collection("machines").document(
                    machine_id).update({"state": 0})

                prep_dict = prep.get().to_dict()

                is_saved = prep_dict["saved"]

                if is_saved:

                    next_time = calculate_next_time(
                        prep_dict["daysOfWeek"], prep_dict["hours"])
                    prep.update({
                        "lastTime": prep_dict["nextTime"],
                        "nextTime": next_time
                    })

                notif_ref = user.collection("notifications").document()

                notif_ref.set({
                    "id": notif_ref.id,
                    "preparation": prep,
                    "state": 2
                })

                print("------ End report_preparation_failed ------")

                return 200
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500

    def create_preparation(self, data: CreatePreparation, id_user: str):
        try:
            print("------- Start create_preparation -------")
            prep = db.collection("users").document(
                id_user).collection("preparations").document()

            coffee = db.collection("coffees").document(data.coffee_id)
            machine = db.collection("machines").document(data.machine_id)

            if coffee.get().exists and machine.get().exists:

                if data.saved:

                    next_time = calculate_next_time(
                        data.days_of_week, data.hours)

                    prep.set({
                        "coffee": coffee,
                        "creationDate": datetime.now(tz=pytz.utc),
                        "daysOfWeek": data.days_of_week,
                        "hours": data.hours,
                        "id": prep.id,
                        "lastTime": datetime.now(tz=pytz.utc),
                        "lastUpdate": datetime.now(tz=pytz.utc),
                        "machine": machine,
                        "name": data.name,
                        "saved": data.saved,
                        "nextTime": next_time,
                        "state": 0
                    })
                else:
                    prep.set({
                        "coffee": coffee,
                        "creationDate": datetime.now(tz=pytz.utc),
                        "id": prep.id,
                        "lastUpdate": datetime.now(tz=pytz.utc),
                        "machine": machine,
                        "nextTime": datetime.strptime(data.next_time, "%Y-%m-%dT%H:%M:%SZ"),
                        "saved": data.saved,
                        "state": 0
                    })
                print("------- End create_preparation -------")
                return 201
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500

    def update_preparation(self, data: UpdatePreparationSaved, id: str, id_user: str):
        try:
            print("------ Start update_preparation ------")

            prepa = db.collection('users').document(
                id_user).collection("preparations").document(id)

            if prepa.get().exists:

                coffee = db.collection('coffees').document(data.coffee_id)

                machine = db.collection('machines').document(data.machine_id)

                if machine.get().exists and coffee.get().exists:

                    next_time = calculate_next_time(
                        data.days_of_week, data.hours, prepa.get().to_dict()["nextTime"])

                    print("Date now  = {} {} and date nexttime =  {} {}".format(datetime.now(
                        tz=pytz.utc), type(datetime.now(tz=pytz.utc)), next_time, type(next_time)))

                    prepa.update({"name": data.name,
                                  "lastUpdate": datetime.now(tz=pytz.utc),
                                  "daysOfWeek": data.days_of_week,
                                  "hours": data.hours,
                                  "nextTime": next_time,
                                  "coffee": coffee,
                                  "machine": machine
                                  })

                    print("------ End update_preparation ------")
                    return 200
                else:
                    return 404
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500

    def delete_preparation(self, id: str, id_user: str):
        try:
            print("------ Start delete_preparation ------")
            prepa = db.collection('users').document(
                id_user).collection("preparations").document(id)
            if prepa.get().exists:
                prepa.delete()
                print("------ End delete_preparation ------")
                return 200
            else:
                return 404
        except Exception as ex:
            print("Error : {}".format(ex))
            return 400


class CoffeeService(ABC):
    def get_coffee(self):
        try:
            print("------ Start get_coffee ------")
            docs = db.collection('coffees').stream()
            print("Get coffees ---> {}".format(docs))
            coffees = []
            for doc in docs:
                dico = doc.to_dict()
                coffees.append(
                    Coffee(id=dico["id"], name=dico["name"], description=dico["description"]))
            print("------ End get_coffee ------")
            return (200, coffees)
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500, coffees

    def get_coffee_by_id(self, id):
        try:
            print("----- Start get_coffee_by_id ----")
            doc = db.collection('coffees').document(id).get()
            if doc.exists:
                dico = doc.to_dict()
                return 200, Coffee(id=dico["id"], name=dico["name"], description=dico["description"])
            else:
                return 404, None
        except Exception as ex:
            print("Error : {}".format(ex))
            return 500


def calculate_next_time(day_of_week: list, hours: list):

    print("---- Start calculate_next_time ------")

    current_date = datetime.now(tz=pytz.utc)

    current_dayofweek = current_date.weekday()  # day = 6
    # daysOfWeek = [4,5,6]

    if len(day_of_week) > 1:
        i = 0
        while current_dayofweek > day_of_week[i]:
            i = i+1

        if i == len(day_of_week) - 1:
            index_wanted_found = 0
        else:
            index_wanted_found = i

        print("Index the closest day of week : {0} so prep_dict[{0}] = {1}".format(
            index_wanted_found, day_of_week[index_wanted_found]))

        next_time = current_date

        while day_of_week[index_wanted_found] != next_time.weekday()+1:
            print("Next time : {} and weekdays : {}".format(
                next_time, next_time.weekday()))

            next_time = next_time + timedelta(days=1)

        print("Next date : {}".format(next_time))

    else:
        next_time = current_date
        while day_of_week[0] != next_time.weekday():
            print("Next time : {} and weekdays : {}".format(
                next_time, next_time.weekday()))

            next_time = next_time + timedelta(days=1)
        print("Next date : {}".format(next_time))

    has_same_date = ((next_time.day == current_date.day) and (
        next_time.month == current_date.month) and (next_time.year == current_date.year))

    print(has_same_date)

    if not has_same_date:
        print("Not the same date")
        splitted_hours = hours[0].split(":")
        hour = int(splitted_hours[0])
        minute = int(splitted_hours[1])
        second = int(splitted_hours[2])

        print("Hour = {} , Minute = {} , Second = {}".format(
            hour, minute, second))

        next_time = datetime(
            next_time.year, next_time.month, next_time.day, hour, minute, second, 0, tzinfo=pytz.utc)

        print("Next time with hour = {}".format(next_time))
    else:
        print("Same date")
        i = 0
        if len(hours) > 1:
            for h in hours:
                splitted_hours = h.split(":")
                hour = int(splitted_hours[0])
                minute = int(splitted_hours[1])
                second = int(splitted_hours[2])

                new_date = current_date.replace(
                    hour=hour, minute=minute, second=second, microsecond=0, tzinfo=pytz.utc)

                if new_date > current_date:
                    next_time = new_date
                    break
        else:
            splitted_hours = hours[0].split(":")
            hour = int(splitted_hours[0])
            minute = int(splitted_hours[1])
            second = int(splitted_hours[2])

            next_time = current_date.replace(
                hour=hour, minute=minute, second=second, microsecond=0, tzinfo=pytz.utc)

        print("Next time with hour = {}".format(next_time))

    return next_time

def convert_to_datetime(date):
    val = date
    year,month,day,hour,minute,second,tzinfo = val.year,val.month,val.day,val.hour, val.minute, val.second, val.tzinfo
    return datetime(year,month,day,hour,minute,second, tzinfo=tzinfo)