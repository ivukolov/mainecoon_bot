from aiogram.fsm.state import State, StatesGroup


class CatForm(StatesGroup):
    name = State()
    gender = State()
    birth_date = State()
    color = State()
    cattery = State()
    price = State()
    contacts = State()
    photo = State()
    approve = State()