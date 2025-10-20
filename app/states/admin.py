from aiogram.fsm.state import State, StatesGroup


class AdminModerateStates(StatesGroup):
    bane = State()
    approve = State()
    reject = State()