""" Baisic telegram commands"""
from aiogram import types

from src.aiogram_app.aiogram_app import dp


@dp.message_handler(commands=["help"])
async def send_welcome(message: types.Message, *args):
    """This handler will be called when user sends `/help` command"""
    await message.answer(
        """
        Bot commands:
        start - initiate bot functions for user
        help - display availble commands
        """
    )
