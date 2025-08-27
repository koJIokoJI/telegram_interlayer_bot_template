import logging

from aiogram.filters import BaseFilter
from aiogram.types import Message

from config.config import settings

logger = logging.getLogger(__name__)


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message):
        if message.from_user.id in settings.admin_ids:
            logger.debug("User is owner/admin")
            return message.from_user.id in settings.admin_ids
