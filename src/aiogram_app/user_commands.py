"""aiogram commands related to users"""
import logging
from aiogram import types
from src.logger import logger

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import (
    escape_markdown,
    format_many_vpn_configs,
    format_vpn_config,
    prepare_user_str,
)
from src.aiogram_app.telegram_auth import api_credentials
from src.db import crud
from src.db.schemas import VpnConfig
from src.fastapi_app import user_routes, admin_routes
from src.fastapi_app import pivpn_wrapper as pivpn
from src.utils.errors.pivpn_errors import PiVpnException


@dp.message_handler(commands=["user", "me"])
async def t_me(message: types.Message):
    """get information about current user from db"""
    # get user info
    user = await crud.find_user_by_telegram_id(message.from_user.id)
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
    user = await crud.get_user_by_telegram_id(message.from_user.id)
    if user.conf_files:
        for config in user.conf_files:
            try:
                _config = pivpn.delete_vpn_config(config.user_name)
                logging.info(f"Vpn config deleted: {_config}")
            except PiVpnException as e:
                logging.error(e)
    response = await user_routes.delete_user(
        message.from_user.id,
        api_credentials,
    )
    if response.status_code == 400:
        await message.answer(
            "User not found, u can create a new one with /start"
        )
    elif response.status_code == 200:
        await message.answer("User deleted")


@dp.message_handler(commands=["remove_config", "del_config"])
async def remove_config(message: types.Message):
    """remove vpn config from user"""

    # get arg as user_name
    user_name = message.get_args()
    if not user_name:
        await message.answer("Please provide config user name")
        return
    # call fastapi to delete user
    response = await user_routes.remove_vpn_config(
        message.from_user.id,
        user_name,
        api_credentials,
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer("VPN config removed")


@dp.message_handler(commands=["add_config", "add_vpn_config"])
async def add_config(message: types.Message):
    """add vpn config to user"""

    # get arg as user_name
    user_name = message.get_args()
    if not user_name:
        await message.answer(
            "Please provide config user name after command\n"
            "/add_config <user_name>"
        )
        return

    file_path = await admin_routes.add_vpn_config(user_name)
    # get config from pivpn_api
    data = await user_routes.get_vpn_config(file_path, api_credentials)

    vpn_config = VpnConfig(
        path=file_path,
        user_name=user_name,
    )
    # call fastapi to delete user
    response = await user_routes.add_vpn_config(
        message.from_user.id,
        vpn_config,
        api_credentials,
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer(
            escape_markdown(format_vpn_config(data, user_name)),
            parse_mode="Markdown",
        )


@dp.message_handler(commands=["list_configs", "list_vpn_configs"])
async def list_configs(message: types.Message):
    """list vpn configs of user"""
    # get user from fastapi
    user = await user_routes.get_user_by_id(
        message.from_user.id,
        api_credentials,
    )
    if not user:
        await message.answer("User not found")
        return
    if not user.conf_files:
        await message.answer("No configs found")
        return
    # conf_files paths from user object
    conf_data: list[tuple[str, str]] = [
        (
            await user_routes.get_vpn_config(
                conf.path,
                api_credentials,
            ),
            conf.user_name,
        )
        for conf in user.conf_files
    ]

    await message.answer(
        escape_markdown(format_many_vpn_configs(conf_data)),
        parse_mode="Markdown",
    )


@dp.message_handler(commands=["balance", "get_balance"])
async def get_balance(message: types.Message):
    """get balance of user"""
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"Balance: {user.balance}\nNext payment: {user.next_payment}"
        )
        return
    await message.answer("User not found")


@dp.message_handler(commands=["redeem", "redeem_code"])
async def redeem_code(message: types.Message):
    """redeem code"""
    code = message.get_args()
    if not code:
        await message.answer("Please provide code\n/redeem <code>")
        return
    response = await user_routes.redeem_code(
        message.from_user.id,
        code,
        credentials=api_credentials,
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer("Code redeemed")


@dp.message_handler(commands=["activate", "activate_subscription"])
async def activate_subscription(message: types.Message):
    """activate subscription"""
    response = await user_routes.activate_subscription(
        message.from_user.id,
        credentials=api_credentials,
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer("Subscription activated")


@dp.message_handler(commands=["deactivate", "deactivate_subscription"])
async def deactivate_subscription(message: types.Message):
    """deactivate subscription"""
    response = await user_routes.deactivate_subscription(
        message.from_user.id,
        credentials=api_credentials,
    )
    if response.status_code == 400:
        await message.answer("User not found")
    elif response.status_code == 200:
        await message.answer("Subscription deactivated")
