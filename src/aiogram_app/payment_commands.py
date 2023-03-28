"""aiogram commands related to payments"""
from aiogram import types

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.telegram_auth import api_credentials
from src.db import crud
from src.db.schemas import VpnConfig
from src.fastapi_app import payment_routes
from src.fastapi_app import pivpn_wrapper as pivpn
from src.utils.errors.pivpn_errors import PiVpnException
from src.locales import get_locale
from src.aiogram_app.message_formatters import format_invoice
from src import (
    PAYMENT_AMOUNT,
    LTC_ADDRESS,
    BTC_ADDRESS,
    ETH_ADDRESS,
    XNO_ADDRESS,
    PHONE_NUMBER,
)


@dp.message_handler(commands=["pay_info"])
async def pay_info_command(message: types.Message):
    _ = get_locale(message)
    await message.answer(
        f'{_("Payment information:")}\n'
        f'{_("*Crypto:*")}\n'
        f'{_("  LTC: ") + LTC_ADDRESS}\n'
        f'{_("  BTC: ") + BTC_ADDRESS}\n'
        f'{_("  ETH: ") + ETH_ADDRESS}\n'
        f'{_("  XNO: ") + XNO_ADDRESS}\n'
        f'{_("*FPS Bank transfer:*")}\n'
        f'{_("Phone: ")+ PHONE_NUMBER}\n'
        f'{_(" Banks: ")}\n'
        f'{_(" - Sber")}\n'
        f'{_(" - Tinkoff")}\n',
        parse_mode=types.ParseMode.MARKDOWN,
    )


@dp.message_handler(commands=["pay"])
async def pay_command(message: types.Message):
    _ = get_locale(message)
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(_("User not found"))
        return
    invoice = await payment_routes.create_user_invoice(
        amount=PAYMENT_AMOUNT,
        user_id=user.telegram_id,
        payment_method="FPS",
    )
    await message.answer(format_invoice(invoice, _))
