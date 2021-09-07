from datetime import datetime
import pytest
from ..modules.response_models import Coffee, Machine
from ..modules.services import MachineService, PreparationService, CoffeeService
import pytz

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
