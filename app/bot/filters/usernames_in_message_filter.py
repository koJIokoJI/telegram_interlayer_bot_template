from aiogram.filters import BaseFilter
from aiogram.types import Message


class HasUsernamesFilter(BaseFilter):
    async def __call__(self, message: Message):
        entities = message.entities or []
        usernames = [
            name.extract_from(message.text)
            for name in entities
            if name.type == "mention"
        ]
        if len(usernames) > 0:
            return {"usernames": usernames}
        return False
