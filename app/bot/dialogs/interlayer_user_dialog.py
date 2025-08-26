import logging

from aiogram.types import CallbackQuery
from aiogram.enums import ChatMemberStatus

from aiogram_dialog import DialogManager, Dialog, Window
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, ListGroup, Url

from redis.asyncio import Redis

from app.bot.dialogs import InterlayerUserSG


logger = logging.getLogger(__name__)


async def subcription_check_button_handler(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    usernames = dialog_manager.dialog_data.get("usernames_list")
    user_is_present = []
    for username in usernames:
        chat_member = await callback.bot.get_chat_member(
            chat_id=username, user_id=callback.from_user.id
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
        return await dialog_manager.switch_to(state=InterlayerUserSG.link)
    return await callback.answer()


async def usernames_getter(dialog_manager: DialogManager, **kwargs):
    redis: Redis = dialog_manager.middleware_data.get("redis")
    usernames: bytes = await redis.get("usernames")
    logger.debug(f"{usernames}, {type(usernames)}")
    usernames = usernames.decode(encoding="utf-8")
    if usernames.find(":"):
        usernames_list = usernames.split(":")
    else:
        usernames_list = [usernames]
    logger.debug(usernames_list)
    dialog_manager.dialog_data.update(usernames_list=usernames_list)
    usernames = []
    for i in range(len(usernames_list)):
        usernames.append({"id": i + 1, "username": usernames_list[i][1:]})
    return {"usernames": usernames}


user_dialog = Dialog(
    Window(
        Const(text="Для продолжения подпишитесь на каналы"),
        ListGroup(
            Url(
                text=Format(text="Канал {item[id]}"),
                url=Format(text="https://t.me/{item[username]}"),
                id="url",
            ),
            id="channels",
            item_id_getter=lambda item: item["id"],
            items="usernames",
        ),
        Button(
            text=Const(text="Проверить"),
            id="subscription_check",
            on_click=subcription_check_button_handler,
        ),
        getter=usernames_getter,
        state=InterlayerUserSG.start,
    ),
    Window(
        Const(text="Вы подписались на канал(-ы)"),
        state=InterlayerUserSG.link,
    ),
)
