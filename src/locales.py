import gettext
from typing import Callable
from aiogram.types import Message, CallbackQuery
from src.db.schemas import User

path = "locale"
gettext.bindtextdomain("messages", path)
gettext.textdomain("messages")
gettext.install(
    "messages",
    path,
)

en = gettext.translation("messages", localedir=path, languages=["en"])
ru = gettext.translation("messages", localedir=path, languages=["ru"])
_ = gettext.gettext


def get_locale(message: Message | CallbackQuery) -> Callable:
    return ru.gettext if message.from_user.language_code == "ru" else en.gettext


def get_user_locale(user: User) -> Callable:
    return ru.gettext if user.locale == "ru" else en.gettext
