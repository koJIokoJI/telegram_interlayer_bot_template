from aiogram.fsm.state import StatesGroup, State


class InterlayerAdminSG(StatesGroup):
    menu = State()
    enter_channel_usernames = State()
    delete_channel_usernames = State()


class InterlayerUserSG(StatesGroup):
    start = State()
    link = State()
