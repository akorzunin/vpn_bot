"""aiogram commands related to users"""
from aiogram import types

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import prepare_user_str
from src.db import crud
from src.fastapi_app import user_routes


@dp.message_handler(commands=["user", "me"])
async def t_me(message: types.Message):
    """get information about current user from db"""
    # get user info
    user = await crud.get_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            "User not found, u can create a new one with /start"
        )
    else:
        # format user in human readable format
        user_str = prepare_user_str(user)
        await message.answer(user_str)


@dp.message_handler(commands=["delete_user", "del_me"])
async def delete_user(message: types.Message):
    """delete user from db"""
    # TODO prompt for confirmation
    # call fastapi to delete user
    response = await user_routes.delete_user(message.from_user.id)
    if response.status_code == 400:
        await message.answer(
            "User not found, u can create a new one with /start"
        )
    elif response.status_code == 200:
        await message.answer("User deleted")


@dp.message_handler(commands=["remove_config", "del_config"])
async def remove_config(message: types.Message, *args):
    """remove vpn config from user"""

    # get arg as user_name
    user_name = message.get_args()
    if not user_name:
        await message.answer("Please provide config user name")
        return
    # call fastapi to delete user
    response = await user_routes.remove_vpn_config(
        message.from_user.id, user_name
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer("VPN config removed")
