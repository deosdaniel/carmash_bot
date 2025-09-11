from aiogram.fsm.state import State, StatesGroup

class OrderCar(StatesGroup):
    name = State()
    phone = State()
    email = State()
    car_model = State()
    budget = State()