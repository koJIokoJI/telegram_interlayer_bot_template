import logging

from aiogram.types import Message
from aiogram.filters import BaseFilter
from aiogram.enums import ChatMemberStatus

from redis.asyncio import Redis


logger = logging.getLogger(__name__)


class IsChannelMemberFilter(BaseFilter):
    async def __call__(self, message: Message, redis: Redis):
        usernames: bytes = await redis.get("usernames")
        logger.debug(f"{usernames}, {type(usernames)}")
        if usernames:
            usernames = usernames.decode(encoding="utf-8")
            if usernames.find(":"):
                usernames_list = usernames.split(":")
            else:
                usernames_list = [usernames]
            user_is_present = []
            for username in usernames_list:
                chat_member = await message.bot.get_chat_member(
                    chat_id=username, user_id=message.from_user.id
                )
                status = ChatMemberStatus(chat_member.status)
                logger.debug(status)
                if status in (
                    ChatMemberStatus.CREATOR,
                    ChatMemberStatus.ADMINISTRATOR,
                    ChatMemberStatus.MEMBER,
                ):
                    user_is_present.append(True)
                else:
                    user_is_present.append(False)
            logger.debug(user_is_present)
            if all(user_is_present):
                return {"channels": usernames_list, "follow_status": True}
            return False
        else:
            return False
