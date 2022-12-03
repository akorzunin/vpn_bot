''' Baisic telegram commands'''
from aiogram import types

from src.aiogram_app.aiogram_app import dp
from src.db import crud
from src.db.schemas import User
from src.fastapi_app import user_routes

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    # find user by telegram id from db
    user = await crud.get_user_by_telegram_id(message.from_user.id)
    # TODO prompt user if they already have vpn account
    # if yes ask for user_name field
    user = User(
        telegram_id=message.from_user.id,
    )
    # create user if its not already exists using fastapi route function
    response = await user_routes.create_user(user)
    # if response is success send user message that he is created
    if response.status_code == 201:
        await message.answer("User created")
    # if response is not ok send message that user already exists
    elif response.status_code == 400:
        await message.answer("User already exists")

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
