""" Baisic telegram commands"""
from aiogram import types
from typing import Callable

from src.aiogram_app.aiogram_app import dp
from src.locales import get_locale, _


@dp.message_handler(commands=["help"])
async def send_welcome(message: types.Message, *args):
    """This handler will be called when user sends `/help` command"""
    # get user fron db

    #  if user active send him active_user_help
    # if not active disabled_user_help
    # else not_registered_user_help
    await message.answer(
        """
        Bot commands:
        start - initiate bot functions for user
        help - display availble commands
        """
    )


def active_user_help(_: Callable = _) -> str:
    return _(
        "Bot commands:\n"
        "/help - show this message\n"
        "/add_vpn_config - Add vpn config to user account\n"
        "/del_config - Delete vpn config from database and from server.\n"
        "/me - info about user\n"
        # "/qr - "
        # "/get_config - "
        "/redeem_code - Redeem code\n"
        "/pay - create invoice\n"
        "/pay_info - get payment informaion\n"
        "/deactivate_subscription - Deactivate subscription for customer.\n"
    )


def disabled_user_help(_: Callable = _) -> str:
    return _(
        "Bot commands:\n"
        "/help - show this message\n"
        "/add_vpn_config - Add vpn config to user account\n"
        "/del_config - Delete vpn config from database and from server.\n"
        "/me - info about user\n"
        "/redeem_code - Redeem code\n"
        "/pay - create invoice\n"
        "/pay_info - get payment informaion\n"
        "/activate_subscription - Activate subscription for customer. Payment will be accepted immediately\n"
    )


def not_registered_user_help(_: Callable = _) -> str:
    return _("Bot commands:\n" "/help - show this message\n" "/start - login")
