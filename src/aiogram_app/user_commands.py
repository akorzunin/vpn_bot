"""aiogram commands related to users"""
from io import BytesIO
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
from src.locales import get_locale


@dp.message_handler(commands=["user", "me"])
async def t_me(message: types.Message):
    """get information about current user from db"""
    _ = get_locale(message)
    # get user info
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(
            _("User not found, u can create a new one with /start")
        )
    else:
        # format user in human readable format
        user_str = prepare_user_str(user, _)
        await message.answer(user_str)


@dp.message_handler(commands=["delete_user", "del_me"])
async def delete_user(message: types.Message):
    """delete user from db"""
    # TODO prompt for confirmation
    # call fastapi to delete user
    _ = get_locale(message)
    user = await crud.get_user_by_telegram_id(message.from_user.id)
    if user.conf_files:
        for config in user.conf_files:
            try:
                _config = pivpn.delete_vpn_config(config.user_name)
                logging.info(f"{_('Vpn config deleted')}: {_config}")
            except PiVpnException as e:
                logging.error(e)
    response = await user_routes.delete_user(
        message.from_user.id,
        api_credentials,
    )
    if response.status_code == 400:
        await message.answer(
            _("User not found, u can create a new one with /start")
        )
    elif response.status_code == 200:
        await message.answer(_("User deleted"))


@dp.message_handler(commands=["remove_config", "del_config"])
async def remove_config(message: types.Message):
    """remove vpn config from user"""
    _ = get_locale(message)
    # get arg as user_name
    user_name = message.get_args()
    if not user_name:
        await message.answer(_("Please provide config user name"))
        return
    # call fastapi to delete user
    response = await user_routes.remove_vpn_config(
        message.from_user.id,
        user_name,
        api_credentials,
    )
    if response.status_code == 400:
        await message.answer(_("User not found"))
    elif response.status_code == 200:
        await message.answer(_("VPN config removed"))


@dp.message_handler(commands=["add_config", "add_vpn_config"])
async def add_config(message: types.Message):
    """add vpn config to user"""
    _ = get_locale(message)
    # get arg as user_name
    user_name = message.get_args()
    if not user_name:
        await message.answer(
            _(
                "Please provide config user name after command\n"
                "/add_config <user_name>"
            )
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
        await message.answer(_("User not found"))
    elif response.status_code == 200:
        document = types.InputFile(
            BytesIO(data.encode()),
            filename=f"{user_name}.conf",
        )
        await message.answer_document(
            document=document,
            caption=escape_markdown(format_vpn_config(data, user_name, _)),
            parse_mode="Markdown",
        )


@dp.message_handler(commands=["get_config", "get_vpn_config"])
async def get_config(message: types.Message):
    """get user vpn config"""
    _ = get_locale(message)
    config_name = message.get_args()
    if not config_name:
        await message.answer(
            _(
                "Please provide config user name after command\n"
                "/get_config <user_name>\n"
                "Or list all configs with command: /list_configs"
            )
        )
        return
    user = await user_routes.get_user_by_id(
        message.from_user.id,
        api_credentials,
    )
    if not user.conf_files:
        await message.answer(_("No configs found"))
        return
    config = next(
        (x for x in user.conf_files if x.user_name == config_name), None
    )
    if not config:
        await message.answer(
            _(
                "Config not found\n"
                "You can add config with command: /add_config <user_name>\n"
                "Or list configs with command: /list_configs\n"
            )
        )
        return
    data = await user_routes.get_vpn_config(config.path, api_credentials)
    document = types.InputFile(
        BytesIO(data.encode()),
        filename=f"{config.user_name}.conf",
    )
    await message.answer_document(
        document=document,
        caption=escape_markdown(format_vpn_config(data, config.user_name, _)),
        parse_mode="Markdown",
    )


@dp.message_handler(commands=["qr", "get_config_qr"])
async def get_config_qr(message: types.Message):
    """get user vpn config"""
    _ = get_locale(message)
    config_name = message.get_args()
    if not config_name:
        await message.answer(
            _(
                "Please provide config user name after command\n"
                "/qr <user_name>\n"
                "Or list all configs with command: /list_configs"
            )
        )
        return
    user = await user_routes.get_user_by_id(
        message.from_user.id,
        api_credentials,
    )
    if not user.conf_files:
        await message.answer(_("No configs found"))
        return
    config = next(
        (x for x in user.conf_files if x.user_name == config_name), None
    )
    if not config:
        await message.answer(
            _(
                "Config not found\n"
                "You can add config with command: /add_config <user_name>\n"
                "Or list configs with command: /list_configs\n"
            )
        )
        return
    data = await admin_routes.get_vpn_config_qr(config.user_name)
    await message.answer_photo(
        data.body_iterator,
        caption=f"{_('QR code for vpn config')} {config.user_name}",
    )


@dp.message_handler(commands=["list_configs", "list_vpn_configs"])
async def list_configs(message: types.Message):
    """list vpn configs of user"""
    _ = get_locale(message)
    # get user from fastapi
    user = await user_routes.get_user_by_id(
        message.from_user.id,
        api_credentials,
    )
    if not user:
        await message.answer(_("User not found"))
        return
    if not user.conf_files:
        await message.answer(_("No configs found"))
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
        escape_markdown(format_many_vpn_configs(conf_data, _)),
        parse_mode="Markdown",
    )


@dp.message_handler(commands=["balance", "get_balance"])
async def get_balance(message: types.Message):
    """get balance of user"""
    _ = get_locale(message)
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"{_('Balance')}: {user.balance}\n{_('Next payment')}: {user.next_payment}"
        )
        return
    await message.answer(_("User not found"))


@dp.message_handler(commands=["redeem", "redeem_code"])
async def redeem_code(message: types.Message):
    """redeem code"""
    _ = get_locale(message)
    code = message.get_args()
    if not code:
        await message.answer(_("Please provide code\n/redeem <code>"))
        return
    response = await user_routes.redeem_code(
        message.from_user.id,
        code,
        credentials=api_credentials,
    )
    if response.status_code == 400:
        await message.answer(_("User not found"))
    elif response.status_code == 200:
        await message.answer(_("Code redeemed"))


@dp.message_handler(commands=["activate", "activate_subscription"])
async def activate_subscription(message: types.Message):
    """activate subscription"""
    _ = get_locale(message)
    response = await user_routes.activate_subscription(
        message.from_user.id,
        credentials=api_credentials,
    )
    if response.status_code == 400:
        await message.answer(_("User not found"))
    elif response.status_code == 200:
        await message.answer(_("Subscription activated"))


@dp.message_handler(commands=["deactivate", "deactivate_subscription"])
async def deactivate_subscription(message: types.Message):
    """deactivate subscription"""
    _ = get_locale(message)
    response = await user_routes.deactivate_subscription(
        message.from_user.id,
        credentials=api_credentials,
    )
    if response.status_code == 400:
        await message.answer(_("User not found"))
    elif response.status_code == 200:
        await message.answer(_("Subscription deactivated"))
