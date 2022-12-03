"""aiogram commands related to users"""
from aiogram import types

from src.aiogram_app.aiogram_app import dp


@dp.message_handler(commands=["user"])
async def start(message: types.Message):
    if 0:
        await message.answer("User already exists")
    else:
        await message.answer("User created")


#  new command w/ execption
@dp.message_handler(commands=["pog"])
async def trial(message: types.Message):
    raise NotImplementedError
