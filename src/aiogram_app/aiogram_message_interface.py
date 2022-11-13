from aiogram import Bot
import os

TOKEN = os.getenv("TOKEN")
operator = Bot(TOKEN)


async def send_message_to_user_by_id(user_id: int, message: str):
    await operator.send_message(
        chat_id=user_id,
        text=message,
    )
