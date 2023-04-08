import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import TelegramAPIError
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from fastapi import HTTPException
from src import ADMIN_ID

API_TOKEN = os.getenv("TOKEN")
# check if token exist else rise error
if not API_TOKEN:
    raise ValueError("TOKEN is not set in .env file")
bot = Bot(API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

# register user_commands
from src.aiogram_app import user_commands

# register baisic commands
from src.aiogram_app import baisic_commands

# register admin commands
from src.aiogram_app import admin_commands

# register login commands
from src.aiogram_app import login_commands

# register payment commands
from src.aiogram_app import payment_commands


@dp.errors_handler(
    exception=TelegramAPIError
)  # handle the cases when this exception raises
async def message_not_modified_handler(update, error):
    logging.error(f"Get error from telegram API: {error}")
    # errors_handler must return True if error was handled correctly
    return True


@dp.errors_handler(exception=HTTPException)
async def http_exception_handler(update: types.Update, error: HTTPException):
    logging.error(f"Get error from httpexception: {error.detail}")
    await bot.send_message(
        update.message.chat.id,
        f"{error.detail}",
    )
    return True


def IsAdminErrorFilter(update: types.Update, error: Exception):
    return update.callback_query.from_user.id == ADMIN_ID


@dp.errors_handler(IsAdminErrorFilter, exception=ValueError)
async def value_error_handler(update: types.Update, error: ValueError):
    logging.error(f"Get error from value error: {error}")
    await update.callback_query.answer(f"{error}", show_alert=True)
    await bot.send_message(
        update.callback_query.message.chat.id,
        f"{error}",
    )
    return True
