from aiogram.filters import BaseFilter
from aiogram.types import Message

from config.config import settings


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        return message.from_user.id in settings.admin_ids
