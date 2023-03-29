from typing import Literal
from src.aiogram_app.aiogram_message_interface import send_message_to_user_by_id
from src.db.crud import get_user_by_telegram_id
from src.db.schemas import User, VpnPayment
from src.locales import get_user_locale


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
    paymen: VpnPayment,
):
    _ = get_user_locale(user)
    message = _(
        "Payment notifiacation\n"
        "User: {}\n"
        "Want to pay {}"
        "Pay comment: {}"
        "Payment creation date: {}"
    )
    await send_message_to_user_by_id(user.telegram_id, message)
