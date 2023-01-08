"""Admin commands: only admin can use them
    admins defined in .env file
"""

from aiogram import types

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import prepare_all_user_str
from src.fastapi_app import admin_routes
from src.db import crud


@dp.message_handler(commands=["get_all_users"])
async def get_all_users(
    message: types.Message,
):
    """"""
    data = await admin_routes.get_all_users()

    await message.answer(prepare_all_user_str(data))


# get_user command
@dp.message_handler(commands=["test_qr"])
async def get_user(
    message: types.Message,
    *args,
):
    """"""
    client_no = message.get_args()
    if not client_no:
        await message.answer("Please provide client name")
        return
    try:
        data = await admin_routes.get_user_qr(client_no)
    except ValueError as e:
        await message.answer(str(e))
        return
    await message.answer_photo(
        data.body_iterator,
        caption=f"QR code for client {client_no}",
    )
