from aiogram.fsm.state import State, StatesGroup


class UserState(StatesGroup):
    waiting_for_image = State()
    waiting_for_language = State()
