import logging

from aiogram.types import Message, CallbackQuery
from aiogram.enums import ContentType

from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import Button, SwitchTo, Multiselect
from aiogram_dialog.widgets.input import TextInput, MessageInput, ManagedTextInput

from redis.asyncio import Redis

from app.bot.dialogs import InterlayerAdminSG


logger = logging.getLogger(__name__)


def usernames_message_check(usernames: str):
    usernames_list = usernames.split(" ")
    if all(name.startswith("@") for name in usernames_list):
        return usernames_list
    raise ValueError


async def text_type_check(
    message: Message, widget: MessageInput, dialog_manager: DialogManager
):
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(text="Пожалуйста, введите юзернейм(-ы) <b>текстом</b>")


async def correct_usernames_check(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    usernames: list[str],
):
    redis: Redis = dialog_manager.middleware_data.get("redis")
    await redis.set("usernames", ":".join(usernames))
    await message.answer(text="Юзернейм(-ы) успешно добалвен(-ы)")
    await dialog_manager.switch_to(state=InterlayerAdminSG.menu)


async def incorrect_usernames_check(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    dialog_manager.show_mode = ShowMode.NO_UPDATE
    await message.answer(
        text="Пожалуйста, введите юзернейм(-ы)(строка/строки, начинающийся/начинающиеся со знака `@`)\n<b>Пример</b>: @ncbl_u_TaHku"
    )


async def switch_to_deletion_window(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    redis: Redis = dialog_manager.middleware_data.get("redis")
    usernames = await redis.get("usernames")
    if usernames:
        await dialog_manager.switch_to(state=InterlayerAdminSG.delete_channel_usernames)
    else:
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        await callback.message.answer(text="Сейчас нет рекламных каналов/ботов")
        await dialog_manager.switch_to(state=InterlayerAdminSG.menu)


async def confirm_deletion_button_handler(
    callback: CallbackQuery, widget: Button, dialog_manager: DialogManager
):
    redis: Redis = dialog_manager.middleware_data.get("redis")
    checked = dialog_manager.find("usernames_list").get_checked()
    usernames_list = dialog_manager.dialog_data.get("usernames_list")
    usernames_to_delete = [usernames_list[int(i) - 1] for i in checked]
    usernames_list = list(set(usernames_list) - set(usernames_to_delete))
    dialog_manager.current_context().widget_data["usernames_list"] = []
    logger.debug(usernames_list)

    await redis.delete("usernames")
    dialog_manager.dialog_data.update(usernames_list=usernames_list)
    await callback.message.answer(text="Юзернеймы удалены")
    dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
    await dialog_manager.switch_to(state=InterlayerAdminSG.menu)


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
        usernames.append({"id": i + 1, "username": usernames_list[i]})
    return {"usernames": usernames}


admin_dialog = Dialog(
    Window(
        Const(text="Админ панель"),
        SwitchTo(
            text=Const(text="Добавить каналы/ботов для подписки пользователем"),
            id="add_channels_for_subscription",
            state=InterlayerAdminSG.enter_channel_usernames,
        ),
        Button(
            text=Const(text="Удалить каналы/ботов для подписки пользователем"),
            id="delete_channels_for_subscription",
            on_click=switch_to_deletion_window,
        ),
        state=InterlayerAdminSG.menu,
    ),
    Window(
        Const(text="Введите юзернейм(-ы) через пробел\n<b>Пример</b>: @ncbl_u_TaHku"),
        TextInput(
            id="usernames",
            type_factory=usernames_message_check,
            on_success=correct_usernames_check,
            on_error=incorrect_usernames_check,
        ),
        MessageInput(func=text_type_check, content_types=ContentType.ANY),
        state=InterlayerAdminSG.enter_channel_usernames,
    ),
    Window(
        Const(text="Выберите юзернейм(-ы)"),
        Multiselect(
            checked_text=Format(text="✅ {item[username]}"),
            unchecked_text=Format(text="{item[username]}"),
            id="usernames_list",
            item_id_getter=lambda item: item["id"],
            items="usernames",
        ),
        Button(
            text=Const(text="Подтвердить"),
            id="confir_deletion",
            on_click=confirm_deletion_button_handler,
        ),
        SwitchTo(text=Const(text="Отмена"), state=InterlayerAdminSG.menu),
        getter=usernames_getter,
        state=InterlayerAdminSG.delete_channel_usernames,
    ),
)
