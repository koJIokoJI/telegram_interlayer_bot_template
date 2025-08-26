from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_dialog import DialogManager, StartMode

from app.bot.filters import IsAdminFilter
from app.bot.dialogs import InterlayerAdminSG


admin_router = Router()
admin_router.message.filter(IsAdminFilter())


@admin_router.message(CommandStart())
async def process_command_start(message: Message, dialog_manager: DialogManager):
    await dialog_manager.start(state=InterlayerAdminSG.menu, mode=StartMode.RESET_STACK)
