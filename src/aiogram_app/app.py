import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, executor, types
from aiogram.utils.exceptions import TelegramAPIError

API_TOKEN = os.getenv("TOKEN")

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.errors_handler(
    exception=TelegramAPIError
)  # handle the cases when this exception raises
async def message_not_modified_handler(update, error):
    logging.error(f"Get error from telegram API: {error}")
    # errors_handler must return True if error was handled correctly
    return True


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    if 0:
        await message.answer("User already exists")
    else:
        await message.answer("User created")


@dp.message_handler(commands=["help"])
async def send_welcome(message: types.Message, *args):
    """This handler will be called when user sends `/start` or `/help` command"""
    await message.answer(
        """
        Bot commands:
        start - initiate bot functions for user
        help - display availble commands
        get_info - get information about user
        docs - get link to docs api
        get_ticker - get information about trade pair [args: pair]
        new_rule - create rule that send notification if it's condition is true [args: pair, tresholdtype, value]
        get_all_symbols - get all info availble abou all pairs
        list_rules - get list of currently active rules for curren user
        del_rule - delete rule from user [args: rule_id]
        """
    )
