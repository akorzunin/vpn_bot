"""aiogram commands related to payments"""
import json
from uuid import uuid4
from aiogram import types
from typing import Callable, Literal

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.telegram_auth import api_credentials
from src.db import crud
from src.db.schemas import UserPayment, UserUpdate, VpnConfig, VpnPaymentId
from src.fastapi_app import payment_routes
from src.fastapi_app import pivpn_wrapper as pivpn
from src.utils.errors.pivpn_errors import PiVpnException
from src.locales import get_locale
from src.aiogram_app.message_formatters import format_invoice_created
from src.aiogram_app import notifications
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from src import (
    ADMIN_ID,
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
        f'{_("  LTC:")} {LTC_ADDRESS}\n'
        f'{_("  BTC:")} {BTC_ADDRESS}\n'
        f'{_("  ETH:")} {ETH_ADDRESS}\n'
        f'{_("  XNO:")} {XNO_ADDRESS}\n'
        f'{_("*FPS Bank transfer:*")}\n'
        f'{_("Phone:")} {PHONE_NUMBER}\n'
        f'{_(" Banks: ")}\n'
        f'{_(" - Sber")}\n'
        f'{_(" - Tinkoff")}\n',
        parse_mode=types.ParseMode.MARKDOWN,
    )


@dp.message_handler(commands=["pay"])
async def pay_command(message: types.Message):
    _ = get_locale(message)
    state = dp.current_state(user=message.from_user.id)
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if not user:
        await message.answer(_("User not registered"))
        return
    builder = InlineKeyboardMarkup()
    if user.pay_comment and user.payment_method and user.last_amount:
        builder.add(
            types.InlineKeyboardButton(
                text=_(
                    "Pay with comment: {user.pay_comment}"
                    " and use method: {user.payment_method}"
                    " amount: {user.last_amount}"
                ).format(user=user),
                callback_data="pay_with_comment_from_db",
            )
        )
    builder.add(
        types.InlineKeyboardButton(
            text=_("Select payment method"),
            callback_data="select_payment_method",
        )
    )
    builder.add(
        types.InlineKeyboardButton(text=_("Cancel"), callback_data="pay_end"),
    )
    await state.set_state("PAY_METHOD")
    await message.answer(
        _(
            "Creating payment invoice:\n"
            "  Enter pay comment (your name or any text to\n"
            "  identify your payment)\n"
            "ex: Ivanov I.\n"
        ),
        reply_markup=builder,
    )


@dp.callback_query_handler(state="PAY_METHOD", text="select_payment_method")
async def select_payment_method_callback(callback: types.CallbackQuery):
    _ = get_locale(callback)
    await callback.answer()
    state = dp.current_state(user=callback.from_user.id)
    builder = InlineKeyboardMarkup()
    builder.add(
        types.InlineKeyboardButton(text=_("Crypto"), callback_data="Crypto")
    )
    builder.add(types.InlineKeyboardButton(text=_("FPS"), callback_data="FPS"))
    await callback.message.answer(
        _("Select payment method"),
        reply_markup=builder,
    )
    await state.set_state("PAY_COMMENT")


@dp.callback_query_handler(state="PAY_CREATE", text="pay_with_comment")
async def pay_with_comment_callback(callback: types.CallbackQuery):
    _ = get_locale(callback)
    await callback.answer()
    state = dp.current_state(user=callback.from_user.id)
    state_data = await state.get_data()
    pay_amount = state_data["amount"]
    pay_comment = state_data["pay_comment"]
    payment_method: Literal["crypto", "FPS"] = (
        "crypto" if state_data["payment_method"] == "Crypto" else "FPS"
    )
    res = await payment_routes.create_user_invoice(
        user_id=callback.from_user.id,
        payment_method=payment_method,
        pay_amount=pay_amount,
        pay_comment=pay_comment,
    )
    invoice = UserPayment(**json.loads(json.loads(res.body.decode())))
    await callback.message.answer(format_invoice_created(invoice, _))
    # update payment data in db
    if user := await crud.get_user_by_telegram_id(callback.from_user.id):
        user_update = UserUpdate(
            payment_method=payment_method,
            last_amount=pay_amount,
            pay_comment=pay_comment,
        )
        await crud.update_user(user.telegram_id, user_update)

    # notify admin
    ...
    await pay_finalize_dialog(callback, _)


@dp.callback_query_handler(state="PAY_METHOD", text="pay_with_comment_from_db")
async def pay_comment_callback(callback: types.CallbackQuery):
    _ = get_locale(callback)
    user = await crud.get_user_by_telegram_id(callback.from_user.id)
    if user.last_amount is None or user.pay_comment is None:
        raise ValueError("last_amount or pay_comment is None")
    res = await payment_routes.create_user_invoice(
        user_id=user.telegram_id,
        payment_method=user.payment_method,
        pay_amount=user.last_amount,
        pay_comment=user.pay_comment,
    )
    invoice = UserPayment(**json.loads(json.loads(res.body.decode())))

    await callback.message.answer(format_invoice_created(invoice, _))
    # notify admin
    await notifications.send_payment_notification_to_admin(
        user,
        invoice,
    )
    await pay_finalize_dialog(callback, _)


@dp.callback_query_handler(
    state="PAY_COMMENT",
    text=["Crypto", "FPS"],
)
async def select_payment_method_crypto_callback(callback: types.CallbackQuery):
    _ = get_locale(callback)
    await callback.answer()
    state = dp.current_state(user=callback.from_user.id)
    await state.set_data({"payment_method": callback.data})
    await callback.message.answer(_("Enter pay comment"))
    await state.set_state("PAY_COMMENT_TEXT")


@dp.message_handler(state="PAY_COMMENT_TEXT")
async def pay_comment_text_message(message: types.Message):
    _ = get_locale(message)
    state = dp.current_state(user=message.from_user.id)
    pay_comment = message.text.strip()
    await state.update_data({"pay_comment": pay_comment})
    await message.answer(_("Enter amount to pay"))
    await state.set_state("PAY_AMOUNT_TEXT")


@dp.message_handler(state="PAY_AMOUNT_TEXT")
async def pay_amount_text_message(message: types.Message):
    _ = get_locale(message)
    state = dp.current_state(user=message.from_user.id)
    amount = message.text.strip()
    if not amount.isdigit():
        await message.answer(_("Amount must be integer"))
        return
    data = await state.get_data()
    pay_comment: str = data["pay_comment"]
    pay_method: str = data["payment_method"]
    builder = InlineKeyboardMarkup()
    builder.add(
        types.InlineKeyboardButton(
            text=_("Confirm payment"),
            callback_data="pay_with_comment",
        )
    )
    builder.add(
        types.InlineKeyboardButton(text=_("Cancel"), callback_data="pay_end")
    )
    await state.update_data({"amount": amount})
    await message.answer(
        text=_(
            "Create payment\n"
            "  method: {pay_method}\n"
            "  comment: {pay_comment}\n"
            "  amount: {amount}"
        ).format(
            pay_method=pay_method,
            pay_comment=pay_comment,
            amount=amount,
        ),
        reply_markup=builder,
    )
    await state.set_state("PAY_CREATE")


@dp.callback_query_handler(state="PAY_METHOD", text="pay_end")
async def pay_cancelled_callback(callback: types.CallbackQuery):
    await pay_end_call(callback)


@dp.callback_query_handler(state="PAY_CREATE", text="pay_end")
async def pay_cancelled_callback_(callback: types.CallbackQuery):
    await pay_end_call(callback)


async def pay_end_call(callback):
    _ = get_locale(callback)
    await callback.answer(_("Payment creation canceled"))
    await callback.message.answer(_("Payment creation canceled"))
    state = dp.current_state(user=callback.from_user.id)
    await state.reset_data()
    await state.reset_state()


async def pay_finalize_dialog(callback: types.CallbackQuery, _: Callable):
    await callback.answer(_("Payment created"))
    state = dp.current_state(user=callback.from_user.id)
    await state.reset_state()
    await state.reset_data()


def IsAdminFilter(callback: types.CallbackQuery):
    return callback.from_user.id == ADMIN_ID


def IsPaymentFilter(callback: types.CallbackQuery):
    return "payment" in callback.data


@dp.callback_query_handler(IsPaymentFilter)
async def admin_callback(callback: types.CallbackQuery):
    _ = get_locale(callback)
    action, *__, payment_id = callback.data.split("_", 2)
    if action == "accept":
        # get payment from db
        payment = await crud.get_paymnet_by_id(VpnPaymentId(payment_id))
        payment = await crud.accept_payment(payment)
        # notify user that payment accepted
        await notifications.send_payment_accepted_notification(
            payment,
        )
        ...

    await callback.answer(_("Admin callback"))
    await callback.message.answer(_("Admin callback"), reply=True)
