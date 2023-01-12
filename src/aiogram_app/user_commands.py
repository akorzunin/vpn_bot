"""aiogram commands related to users"""
from aiogram import types

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import (
    escape_markdown,
    format_many_vpn_configs,
    format_vpn_config,
    prepare_user_str,
)
from src.db import crud
from src.db.schemas import VpnConfig
from src.fastapi_app import user_routes, admin_routes
from src.fastapi_app import pivpn_wrapper as pivpn


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


@dp.message_handler(commands=["add_config", "add_vpn_config"])
async def add_config(message: types.Message, *args):
    """add vpn config to user"""

    # get arg as user_name
    user_name = message.get_args()
    if not user_name:
        await message.answer("Please provide config user name")
        return

    file_path = await admin_routes.add_client(user_name)
    # get config from pivpn_api
    data = await user_routes.get_vpn_config(file_path)

    vpn_config = VpnConfig(
        path=file_path,
        user_name=user_name,
        pivpn_id=123,
        private_key="str",
        ip="str",
        shared_key="str",
    )
    # call fastapi to delete user
    response = await user_routes.add_vpn_config(
        message.from_user.id, vpn_config
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer(
            escape_markdown(format_vpn_config(data, user_name)),
            parse_mode="Markdown",
        )


@dp.message_handler(commands=["list_configs", "list_vpn_configs"])
async def list_configs(
    message: types.Message,
):
    """list vpn configs of user"""
    # get user from fastapi
    user = await user_routes.get_user_by_id(message.from_user.id)
    if not user:
        await message.answer("User not found")
        return
    if not user.conf_files:
        await message.answer("No configs found")
        return
    # conf_files paths from user object
    conf_data: list[tuple[str, str]] = [
        (await user_routes.get_vpn_config(conf.path), conf.user_name)
        for conf in user.conf_files
    ]

    await message.answer(
        escape_markdown(format_many_vpn_configs(conf_data)),
        parse_mode="Markdown",
    )
