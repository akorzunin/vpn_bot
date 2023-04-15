from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup

from src.aiogram_app.aiogram_message_interface import (
    send_message_to_user_by_id,
    operator,
)
from src.db.crud import get_user_by_telegram_id
from src.db.schemas import User, UserPayment, VpnPayment
from src.locales import get_user_locale
from src import ADMIN_ID


async def send_payment_notification(user: User):
    _ = get_user_locale(user)
    message = _(
        "Payment notification:\n"
        "  Balance: {user.balance}\n"
        "  Next payment: {user.next_payment}"
    ).format(user=user)
    await send_message_to_user_by_id(user.telegram_id, message)


async def send_cancel_subscribtion_notification(
    user: User,
    reason: str | None = None,
):
    _ = get_user_locale(user)
    message = _("Subscription canceled")
    if reason:
        message += _("\nReason: {reason}").format(reason=reason)
    await send_message_to_user_by_id(user.telegram_id, message)


async def send_payment_notification_to_admin(
    user: User,
    payment: UserPayment,
):
    _ = get_user_locale(user)
    message = _(
        "FOR ADMIN:\n"
        "Incoming Payment notification\n"
        "id: {payment.id}\n"
        "User: {user.telegram_id}\n"
        "Amount: {payment.amount}\n"
        "Pay comment: {payment.pay_comment}\n"
        "Payment creation date: {payment.date_created}\n"
    ).format(user=user, payment=payment)
    builder = InlineKeyboardMarkup()
    builder.add(
        types.InlineKeyboardButton(
            text=_("Accept"),
            callback_data=f"accept_payment_{payment.id}",
        ),
        types.InlineKeyboardButton(
            text=_("Reject"),
            callback_data=f"reject_payment_{payment.id}",
        ),
    )
    await operator.send_message(
        chat_id=ADMIN_ID,
        text=message,
        reply_markup=builder,
    )


async def send_payment_accepted_notification(payment: VpnPayment):
    user = await get_user_by_telegram_id(payment.user_id)
    _ = get_user_locale(user)
    message = _(
        "Payment accepted\n"
        "Amount: {payment.amount}\n"
        "Pay comment: {payment.pay_comment}\n"
        "Payment creation date: {payment.date_created}\n"
    ).format(payment=payment)
    await send_message_to_user_by_id(user.telegram_id, message)
