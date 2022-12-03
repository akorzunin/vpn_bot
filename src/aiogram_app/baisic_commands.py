''' Baisic telegram commands'''
from aiogram import types

from src.aiogram_app.aiogram_app import dp

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
