"""Allow other app in event loop use telegram api to send messages to users"""


from aiogram import Bot
import os

if TOKEN := os.getenv("TOKEN"):
    operator = Bot(TOKEN)
else:
    raise ValueError("TOKEN is not set in .env file")


async def send_message_to_user_by_id(user_id: int, message: str):
    await operator.send_message(
        chat_id=user_id,
        text=message,
    )
