from datetime import datetime
import pytest
from ..modules.response_models import Coffee, Machine
from ..modules.services import MachineService, PreparationService, CoffeeService
import pytz


class TestMachine:
    NB_MACHINES = 1
    USER_ID = "9KFeGrJB7mQqMVX4RISBGRgI2oJ3"
    MACHINE = Machine(
        id="pcwCjNM56YGyxrBPDfEs",
        state=0,
        type=0,
        name="Machine de l'entreprise mise a jour v3",
        last_update=datetime(2021, 6, 18, 8, 0, 0, tzinfo=pytz.utc),
        creation_date=datetime(2021, 6, 18, 8, 0, 0, tzinfo=pytz.utc)
    )

    def test_get_machines(self):
        print(
            f"The size of returned list machines is {len(MachineService().get_machines(self.USER_ID)[1])} whereas it should be {self.NB_MACHINES}")
        assert len(MachineService().get_machines(
            self.USER_ID)[1]) == self.NB_MACHINES


    def test_get_machine_by_id(self):
        id = "pcwCjNM56YGyxrBPDfEs"
        real_machine: Machine = MachineService().get_machine_by_id(id, self.USER_ID)[1]
        print(
            f"The machine returned is {real_machine} whereas it should be {self.MACHINE}")
        assert real_machine.id == self.MACHINE.id
        assert real_machine.name == self.MACHINE.name
        assert real_machine.creation_date == self.MACHINE.creation_date
        assert real_machine.last_update == self.MACHINE.last_update
        assert real_machine.state == self.MACHINE.state
        assert real_machine.type == self.MACHINE.type


class TestPreparation:
    USER_ID = "9KFeGrJB7mQqMVX4RISBGRgI2oJ3"
    DATE_LAST_PREP = datetime(2021, 6, 23, 10, 0, 0, tzinfo=pytz.utc)

    def test_get_last_preparation(self):
        last_prep = PreparationService().get_last_preparation(
            self.USER_ID)[1].last_time
        year, month, day, hour, minute, second, tzinfo = last_prep.year, last_prep.month, last_prep.day, last_prep.hour, last_prep.minute, last_prep.second, last_prep.tzinfo
        print(
            f"Date return is {last_prep} where it should be {self.DATE_LAST_PREP} ")
        assert datetime(year, month, day, hour, minute, second,
                        tzinfo=tzinfo) == self.DATE_LAST_PREP


class TestCoffee:
    NB_COFFEE = 17
    COFFEE = Coffee(
        id="G1ei7fFc9wiOosQvPOuM",
        description="Pour tous les amateurs de chocolat, vous tomberez amoureux d’un moka (ou peut-être l’avez-vous déjà). Le moka est une boisson espresso au chocolat avec du lait et de la mousse cuits à la vapeur.",
        name="Moka"
    )


    def test_get_coffees(self):
        real_nb_coffees = len(CoffeeService().get_coffee()[1])
        print(
            f"The size of returned list coffees is {real_nb_coffees} whereas it should be {self.NB_COFFEE}")
        assert real_nb_coffees == self.NB_COFFEE


    def test_get_coffee(self):
        id = "G1ei7fFc9wiOosQvPOuM"
        real_coffee: Coffee = CoffeeService().get_coffee_by_id(id)[1]
        print(f"Coffee returned {real_coffee} is not equal to {self.COFFEE}")
        assert real_coffee.id == self.COFFEE.id
        assert real_coffee.name == self.COFFEE.name
        assert real_coffee.description == self.COFFEE.description
