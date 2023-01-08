import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import TelegramAPIError

API_TOKEN = os.getenv(
    "TOKEN",
)
# check if token exist else rise error
if not API_TOKEN:
    raise ValueError("TOKEN is not set in .env file")
bot = Bot(API_TOKEN)
dp = Dispatcher(bot)

# register user_commands
from src.aiogram_app import user_commands

# register baisic commands
from src.aiogram_app import baisic_commands

# register admin commands
from src.aiogram_app import admin_commands


@dp.errors_handler(
    exception=TelegramAPIError
)  # handle the cases when this exception raises
async def message_not_modified_handler(update, error):
    logging.error(f"Get error from telegram API: {error}")
    # errors_handler must return True if error was handled correctly
    return True
