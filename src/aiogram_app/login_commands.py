from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup

from src.aiogram_app.aiogram_app import dp
from src.db import crud
from src.db.schemas import User
from src.fastapi_app import user_routes


@dp.message_handler(commands=["start"])
async def restart(message: types.Message):
    builder = InlineKeyboardMarkup()
    builder.add(
        types.InlineKeyboardButton(
            text="Login w/ username", callback_data="login_username"
        ),
    )
    builder.add(
        types.InlineKeyboardButton(
            text="Login w/ invitation code", callback_data="login_code"
        ),
    )
    builder.add(
        types.InlineKeyboardButton(text="Cancel", callback_data="login_end"),
    )
    state = dp.current_state(user=message.from_user.id)
    await state.set_state("LOGIN_START")
    await message.answer(
        "Select a method to login. "
        "If you don't use vpn yet, please use username method",
        reply_markup=builder,
    )


@dp.callback_query_handler(state="LOGIN_START", text="login_username")
async def login_username(callback: types.CallbackQuery):
    await callback.message.answer("Enter your username")
    state = dp.current_state(user=callback.from_user.id)
    await state.set_state("LOGIN_USERNAME")
    await callback.answer()


@dp.callback_query_handler(state="LOGIN_START", text="login_code")
async def login_code(callback: types.CallbackQuery):
    await callback.message.answer("Enter your code")
    state = dp.current_state(user=callback.from_user.id)
    await state.set_state("LOGIN_CODE")
    await callback.answer()


@dp.message_handler(state="LOGIN_USERNAME")
async def check_login_username(message: types.Message):
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            f"You already have an account w/ username {user.user_name} "
            "U can use ... commands"
        )
        await end_login_dialog(message)
        return
    user_name = message.text.strip() or message.from_user.username
    user = User(
        telegram_id=message.from_user.id,
        user_name=user_name,
    )
    response = await user_routes.create_user(user)
    # if response is success send user message that he is created
    if response.status_code == 201:
        await message.reply(
            f"User {user.user_name} created U can use ... commands", reply=False
        )
        await end_login_dialog(message)
    # if response is not ok send message that user already exists
    elif response.status_code == 400:
        await message.reply(
            f"User {user.user_name} already exists", reply=False
        )


@dp.callback_query_handler(
    state=["LOGIN_USERNAME", "LOGIN_START"], text="login_end"
)
async def login_end(callback: types.CallbackQuery):
    await callback.message.answer("Login dialog ended")
    state = dp.current_state(user=callback.from_user.id)
    await state.reset_state()
    await callback.answer()


async def end_login_dialog(message: types.Message):
    await message.reply("Login dialog ended", reply=False)
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
