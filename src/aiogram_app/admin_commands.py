"""Admin commands: only admin can use them
    admins defined in .env file
"""

from aiogram import types
from fastapi.security import HTTPBasicCredentials

from src.aiogram_app.aiogram_app import dp
from src.aiogram_app.message_formatters import (
    format_speed_test_data,
    prepare_all_user_str,
)
from src.aiogram_app.telegram_auth import login_admin
from src.db.schemas import Money
from src.fastapi_app import admin_routes
from src.db import crud
from src.fastapi_app.auth import security


@dp.message_handler(commands=["add_client", "add_vpn_config"])
async def add_vpn_config(
    message: types.Message,
):
    """"""
    vpn_config_name = message.get_args()
    if not vpn_config_name:
        await message.answer("Please provide vpn config name")
        return
    data = await admin_routes.add_client(vpn_config_name)

    await message.answer(
        f"Vpn config {vpn_config_name} created\n" f"Config path: {data}"
    )


@dp.message_handler(commands=["backup_vpn_data"])
async def backup_vpn_data(
    message: types.Message,
):
    """"""
    data = await admin_routes.backup_vpn_data(login_admin(message.from_user.id))
    await message.answer(data)


@dp.message_handler(commands=["disable_client", "disable_vpn_config"])
async def disable_vpn_config(
    message: types.Message,
):
    """"""
    vpn_config_name = message.get_args()
    if not vpn_config_name:
        await message.answer("Please provide vpn config name")
        return
    data = await admin_routes.disable_client(vpn_config_name)

    await message.answer(f"Vpn config {vpn_config_name} disabled\n")


@dp.message_handler(commands=["enable_client", "enable_vpn_config"])
async def enable_vpn_config(
    message: types.Message,
):
    """"""
    vpn_config_name = message.get_args()
    if not vpn_config_name:
        await message.answer("Please provide vpn config name")
        return
    data = await admin_routes.enable_client(vpn_config_name)

    await message.answer(f"Vpn config {vpn_config_name} enabled\n")


@dp.message_handler(commands=["list_clients", "list_pivpn_users"])
async def list_pivpn_users(
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


@dp.message_handler(commands=["test_qr"])
async def test_qr(
    message: types.Message,
):
    """"""
    client_no = message.get_args()
    if not client_no:
        await message.answer("Please provide vpn config name")
        return
    try:
        data = await admin_routes.get_user_qr(client_no)
    except ValueError as e:
        await message.answer(str(e))
        return
    await message.answer_photo(
        data.body_iterator,
        caption=f"QR code for vpn config {client_no}",
    )


@dp.message_handler(commands=["speed_test"])
async def speed_test(
    message: types.Message,
):
    """"""
    await message.answer("Running speed test...")
    data = await admin_routes.speed_test()
    await message.answer(format_speed_test_data(data))


@dp.message_handler(commands=["create_payment"])
async def create_payment(
    message: types.Message,
):
    """Makes a payment for a user"""
    if raw_args := message.get_args():
        args = raw_args.split()
        if len(args) != 2:
            await message.answer("Please provide user name and amount")
            return
        user_name, amount = args

        res = await admin_routes.create_payment(
            Money(amount),
            user_name,
        )
        if res.status_code == 200:
            await message.answer("Payment created")
        else:
            await message.answer("Payment not created")


@dp.message_handler(commands=["create_invoice"])
async def create_invoice(
    message: types.Message,
):
    """Manually create an invoice for user"""
    if raw_args := message.get_args():
        args = raw_args.split()
        if len(args) != 2:
            await message.answer("Please provide user name and amount")
            return
        user_name, amount = args

        response = await admin_routes.create_invoice(
            Money(amount),
            user_name,
        )
        if response:
            await message.answer("Invoice created")
        else:
            await message.answer("Invoice not created")
