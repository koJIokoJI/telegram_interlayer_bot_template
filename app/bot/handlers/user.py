import logging

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart

from aiogram_dialog import DialogManager, StartMode

from redis.asyncio import Redis

from app.bot.filters import IsChannelMemberFilter
from app.bot.dialogs import InterlayerUserSG


logger = logging.getLogger(__name__)
user_router = Router()


@user_router.message(CommandStart(), IsChannelMemberFilter())
async def process_followed_start_command(message: Message):
    await message.answer(text="https://t.me/+4Jr3Ux58TCowODdi")


@user_router.message(CommandStart())
async def process_unfollowed_start_command(
    message: Message, dialog_manager: DialogManager, redis: Redis
):
    usernames = await redis.get("usernames")
    if usernames:
        await dialog_manager.start(
            state=InterlayerUserSG.start, mode=StartMode.RESET_STACK
        )
    else:
        await message.answer(text="https://t.me/+4Jr3Ux58TCowODdi")
