"""Admin commands: only admin can use them
    admins defined in .env file
"""

from aiogram import types
from fastapi.security import HTTPBasicCredentials

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import prepare_all_user_str
from src.aiogram_app.telegram_auth import login_admin
from src.fastapi_app import admin_routes
from src.db import crud
from src.fastapi_app.auth import security


@dp.message_handler(commands=["add_client"])
async def add_client(
    message: types.Message,
    *args,
):
    """"""
    vpn_client_name = message.get_args()
    if not vpn_client_name:
        await message.answer("Please provide client name")
        return
    data = await admin_routes.add_client(vpn_client_name)

    await message.answer(
        f"Vpn client {vpn_client_name} created\n" f"Config path: {data}"
    )


@dp.message_handler(commands=["backup_clients"])
async def backup_clients(
    message: types.Message,
):
    """"""
    data = await admin_routes.backup_clients(login_admin(message.from_user.id))
    await message.answer(data)


@dp.message_handler(commands=["disable_client"])
async def disable_client(
    message: types.Message,
    *args,
):
    """"""
    vpn_client_name = message.get_args()
    if not vpn_client_name:
        await message.answer("Please provide client name")
        return
    data = await admin_routes.disable_client(vpn_client_name)

    await message.answer(f"Vpn client {vpn_client_name} disabled\n")


@dp.message_handler(commands=["enable_client"])
async def enable_client(
    message: types.Message,
    *args,
):
    """"""
    vpn_client_name = message.get_args()
    if not vpn_client_name:
        await message.answer("Please provide client name")
        return
    data = await admin_routes.enable_client(vpn_client_name)

    await message.answer(f"Vpn client {vpn_client_name} enabled\n")


@dp.message_handler(commands=["list_clients"])
async def list_clients(
    message: types.Message,
):
    """"""
    data = await admin_routes.list_clients()
    await message.answer(str(data))


@dp.message_handler(commands=["pivpn_user"])
async def pivpn_user(
    message: types.Message,
):
    """"""
    data = await admin_routes.pivpn_user()
    await message.answer(data)


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


@dp.message_handler(commands=["speed_test"])
async def speed_test(
    message: types.Message,
):
    """"""
    data = await admin_routes.speed_test()
    await message.answer(str(data))
