"""Admin commands: only admin can use them
    admins defined in .env file
"""

from aiogram import types

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import prepare_all_user_str
from src.fastapi_app import admin_routes


@dp.message_handler(commands=["get_all_users"])
async def get_all_users(
    message: types.Message,
):
    """"""
    data = await admin_routes.get_all_users()

    await message.answer(prepare_all_user_str(data))
