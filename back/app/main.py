from typing import Any, List
from fastapi.params import Depends
import uvicorn
from fastapi import FastAPI, status, Response
from .modules.response_models import CreatePreparation, MachineCreate, PreparationSaved, \
    UpdatePreparationSaved, UserAuthentication, MachineUpdate, Machine, Coffee, UserRefreshToken
from .modules.services import UserService, MachineService, PreparationService, CoffeeService
from .auth.check_auth import JWTBearer


app = FastAPI(title="DigikofyAPI")


###### USER ROUTE ########

@app.post("/register", status_code=status.HTTP_201_CREATED, tags=["User"])
async def register(data: UserAuthentication, response: Response):
    """
        Route to register the user in the database

        Args:
            data (UserAuthentication): [Information needed to register the user]
            response (Response): [Response returned (status code)]
    """
    code = UserService().create_user(data)
    if code == 201:
        print('Sucessfully created new user')
    elif code == 409:
        print("An user with this email address already exists")
        response.status_code = status.HTTP_409_CONFLICT
    else:
        print("Something went wrong")
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

@app.delete("/delete", status_code=status.HTTP_200_OK, tags=["User"])
async def delete(response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route to delete the user

        Args:
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = UserService().delete_user(id_user)
    if code != 200:
        response.status_code = status.HTTP_400_BAD_REQUEST


@app.post("/login", status_code=status.HTTP_200_OK, tags=["User"])
async def login(data: UserAuthentication, response: Response):
    """
        Route to log in the user

        Args:
            data (UserAuthentication): [Information needed to log in]
            response (Response): [Response returned (status code)]

        Returns:
            [Object]: [Object containing id token, refresh_token]
    """
    res = UserService().log_in_user(data)
    if res is not None:
        return res
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED

@app.post("/refreshToken", status_code=status.HTTP_200_OK, tags=["User"])
async def refresh_token(data : UserRefreshToken, response : Response):
    """
        Route to get a new id token with the refresh token given

        Args:
            data (UserRefreshToken): [Information needed to get a new id token]
            response (Response): [Response returned (status code)]

        Returns:
            [Object]: [Object containing id token, refresh_token]
    """
    res,code = UserService().get_new_token(data)
    if res is not None:
        return res
    elif code == 403:
        response.status_code = status.HTTP_403_FORBIDDEN

@app.post("/revoke", status_code=status.HTTP_200_OK, tags=["User"])
async def revoke_refresh_token(data : UserRefreshToken):
    """
        Route to log out and revoke the refresh token

        Args:
            data (UserRefreshToken): [Information needed to revoke refresh token]
    """
    UserService().revoke_refresh_token(data)

###### MACHINE'S ROUTE ############


@app.post("/machine", status_code=status.HTTP_201_CREATED, tags=["Machine"])
async def add_machine(data: MachineCreate, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route to connect the user to a new machine to the database

        Args:
            data (MachineCreate): [Information needed to connect the user to a new machine]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = MachineService().create_machine(data, id_user)
    print(code)
    if code != 201:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/machines", status_code=status.HTTP_200_OK, response_model=List[Machine], tags=["Machine"])
async def get_machines(response: Response, id_user: str = Depends(JWTBearer())):
    """
        Route that returns all machines available

        Args:
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
        Returns:
            [List[Machine]]: [List of machines available]
    """

    print(f"Id user : {id_user}")
    (code, data) = MachineService().get_machines(id_user)

    print(code)
    if code == 200:
        return data
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/machine/{id}", status_code=status.HTTP_200_OK, response_model=Machine, tags=["Machine"])
async def get_machine(id: str, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route that returns machine with the given id

        Args:
            id (str): [Id machine]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
        Returns:
            [Machine]: [Machine with the given id]
    """
    (code, data) = MachineService().get_machine_by_id(id, id_user)
    print(code)
    if code == 200:
        return data
    elif code == 404:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.put("/machine/{id}", status_code=status.HTTP_200_OK, tags=["Machine"])
async def update_machine(id: str, data: MachineUpdate, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route to update a machine's name that has the given id

        Args:
            id (str): [Id machine]
            data (MachineUpdate): [Information needed to update the machine's name]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = MachineService().update_machine(id, data, id_user)
    if code == 200:
        print("Machine's name update successfully")
    else:
        print("Name not found")
        response.status_code = status.HTTP_404_NOT_FOUND


@app.delete("/machine/{id}", status_code=status.HTTP_200_OK, tags=["Machine"])
async def delete_machine(id: str, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route to delete a machine

        Args:
            id (str): [Id machine]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = MachineService().delete_machine(id, id_user)
    if code != 200 and code != 500:
        response.status_code = status.HTTP_404_NOT_FOUND
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


######## COFFEE'S ROUTE ##########


@app.get("/coffees", status_code=status.HTTP_200_OK, response_model=List[Coffee], tags=["Coffee"])
async def get_coffee(response: Response):
    """
        Route that returns all coffees

        Args:
            response (Response): [Response returned (status code)]
        Returns:
            [List[Coffee]]: [List of coffees]
    """
    (code, data) = CoffeeService().get_coffee()
    print(code)
    if code == 200:
        return data
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/coffee/{id}", status_code=status.HTTP_200_OK, response_model=Coffee, tags=["Coffee"])
async def get_coffee_by_id(id: str, response: Response):
    """
        Route that return the coffee with the given id

        Args:
            id (str): [Id coffee]
            response (Response): [Response returned (status code)]
        Returns:
            [Coffee]: [Coffee with the given id]
    """
    (code, data) = CoffeeService().get_coffee_by_id(id)
    print(code, data)
    if code == 200:
        return data
    elif code == 404:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


###### PREPARATION'S ROUTE ##########

@app.post("/preparation", status_code=status.HTTP_201_CREATED, tags=["Preparation"])
async def add_preparation(data: CreatePreparation, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route to add a new order

        Args:
            data (CreatePreparation): [Information needed to create a new order]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = PreparationService().create_preparation(data, id_user)
    print(code)
    if code != 201 and code != 500:
        response.status_code = status.HTTP_404_NOT_FOUND
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/preparations", status_code=status.HTTP_200_OK, tags=["Preparation"], response_model=List[Any])
async def get_preparations(response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route that retrieve all user's orders

        Args:
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
        Returns:
            [List[Preparation]]: [List of orders that can be saved or not]
    """
    code, preparations = PreparationService().get_preparation(id_user)
    if code == 200:
        return preparations
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.put("/preparation/{id}", status_code=status.HTTP_200_OK, tags=["Preparation"])
async def update_preparation(id: str, data: UpdatePreparationSaved, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route that updates an order with the given id and with the given data

        Args:
            id (str): [Id order]
            data (UpdatePreparationSaved): [Information needed to update an order]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = PreparationService().update_preparation(data, id, id_user)
    print(code)
    if code != 200 and code != 500:
        response.status_code = status.HTTP_404_NOT_FOUND
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.delete("/preparation/{id}", status_code=status.HTTP_200_OK, tags=["Preparation"])
async def delete_preparation(id: str, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route that deletes an order with the given id

        Args:
            id (str): [Id order]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = PreparationService().delete_preparation(id, id_user)
    print(code)
    if code != 200 and code != 500:
        response.status_code = status.HTTP_404_NOT_FOUND
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

####### PREPARATION MACHINE'S ROUTE ##########

@app.get("/preparation/next", status_code=status.HTTP_200_OK, tags=["Preparation"], response_model=Any)
async def get_next_preparation(response : Response, id_user : str = Depends(JWTBearer())):
    code, preparation = PreparationService().get_next_preparation(id_user)
    if code == 200:
        return preparation
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

@app.get("/preparation/last", status_code=status.HTTP_200_OK, tags=["Preparation"], response_model=PreparationSaved)
async def get_next_preparation(response : Response, id_user : str = Depends(JWTBearer())):
    code, preparation = PreparationService().get_last_preparation(id_user)
    if code == 200:
        return preparation
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

@app.get("/preparation/{id}/started", status_code=status.HTTP_200_OK, tags=["Preparation"])
async def report_preparation_started(id: str, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route that adds a report to inform the user that the order has started

        Args:
            id (str): [Id order]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = PreparationService().report_preparation_started(id, id_user)
    print(code)
    if code != 200 and code != 500:
        response.status_code = status.HTTP_400_BAD_REQUEST
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/preparation/{id}/succeeded", status_code=status.HTTP_200_OK, tags=["Preparation"])
async def report_preparation_succeeded(id: str, response: Response,  id_user: str = Depends(JWTBearer())):
    """
        Route that adds a report to inform the user that the order has succeeded

        Args:
            id (str): [Id order]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = PreparationService().report_preparation_succeeded(id, id_user)
    print(code)
    if code != 200 and code != 500:
        response.status_code = status.HTTP_400_BAD_REQUEST
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/preparation/{id}/failed", status_code=status.HTTP_200_OK, tags=["Preparation"])
async def report_preparation_failed(id: str, response: Response,  id_user: str = Depends(JWTBearer())):
    """    
        Route that adds a report to inform the user that the order has failed

        Args:
            id (str): [Id order]
            response (Response): [Response returned (status code)]
            id_user (str, optional): [Id user returned after checking the token used]. Defaults to Depends(JWTBearer()).
    """
    code = PreparationService().report_preparation_failed(id, id_user)
    print(code)
    if code != 200 and code != 500:
        response.status_code = status.HTTP_400_BAD_REQUEST
    elif code == 500:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/preparation/machine/{id}", status_code=status.HTTP_200_OK, response_model=List[Any], tags=["Preparation"])
async def get_preparation_machine(id: str, response: Response):
    """
        Route that retrieves all preparations that are programmed for a future time with given machine id

        Args:
            id (str): [Id machine]
            response (Response): [Response returned (status code)]
        Returns:
            [List[Preparation]]: [List of orders (saved or not)]
    """
    code, preparations = PreparationService().get_preparation_machine(id)
    if code == 200:
        return preparations
    elif code == 404:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


@app.get("/preparation/nextcoffee/{id}", status_code=status.HTTP_200_OK, response_model=List[Any], tags=["Preparation"])
async def get_preparation_next_coffee(id: str, response: Response):
    """
        Route that returns late coffees to be prepared 
        
        Args:
            id (str): [Machine's id]
            response (Response): [Response returned (status code)]
        Returns:
            [List[Preparation]]: [List of orders (saved or not)]
    """
    code, preparations = PreparationService().get_preparation_next_coffee(id)
    if code == 200:
        return preparations
    elif code == 404:
        response.status_code = status.HTTP_404_NOT_FOUND
    else:
        response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
