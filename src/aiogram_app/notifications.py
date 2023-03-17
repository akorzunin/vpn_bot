from src.aiogram_app.aiogram_message_interface import send_message_to_user_by_id
from src.db.crud import get_user_by_telegram_id
from src.db.schemas import User


async def send_payment_notification(user: User):
    message = (
        "Payment notification:\n"
        f"  Balance: {user.balance}\n"
        f"  Next payment: {user.next_payment}"
    )
    await send_message_to_user_by_id(user.telegram_id, message)


async def send_cancel_subscribtion_notification(
    user_id: int,
    reason: str | None = None,
):
    message = "Subscription canceled"
    if reason:
        message += f"\nReason: {reason}"
    await send_message_to_user_by_id(user_id, message)
