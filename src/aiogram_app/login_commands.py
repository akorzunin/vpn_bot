from aiogram import types
from aiogram.types.inline_keyboard import InlineKeyboardMarkup
from fastapi import HTTPException

from src.aiogram_app.aiogram_app import dp
from src.db import crud
from src.db.schemas import User
from src.fastapi_app import user_routes
from src.aiogram_app.telegram_auth import api_credentials
from src.locales import get_locale


@dp.message_handler(commands=["start"])
async def login_start(message: types.Message):
    _ = get_locale(message)
    builder = InlineKeyboardMarkup()
    builder.add(
        types.InlineKeyboardButton(
            text=_("Login with username"), callback_data="login_username"
        ),
    )
    builder.add(
        types.InlineKeyboardButton(
            text=_("Login with invitation code"), callback_data="login_code"
        ),
    )
    builder.add(
        types.InlineKeyboardButton(text=_("Cancel"), callback_data="login_end"),
    )
    state = dp.current_state(user=message.from_user.id)
    if user := await crud.find_user_by_telegram_id(message.from_user.id):
        await message.answer(
            _(
                "You already have an account with username {user.user_name} "
                "You can use /help to see available commands"
            ).format(user=user)
        )
        await end_login_dialog(message)
        return
    await state.set_state("LOGIN_START")
    await message.answer(
        _(
            "Select a method to login. "
            "If you don't use vpn yet, please use username method"
        ),
        reply_markup=builder,
    )


@dp.callback_query_handler(state="LOGIN_START", text="login_username")
async def login_username(callback: types.CallbackQuery):
    _ = get_locale(callback)
    await callback.message.answer(_("Enter your username"))
    state = dp.current_state(user=callback.from_user.id)
    await state.set_state("LOGIN_USERNAME")
    await callback.answer()


@dp.callback_query_handler(state="LOGIN_START", text="login_code")
async def login_code(callback: types.CallbackQuery):
    _ = get_locale(callback)
    await callback.message.answer(_("Enter your code"))
    state = dp.current_state(user=callback.from_user.id)
    await state.set_state("LOGIN_CODE")
    await callback.answer()


@dp.message_handler(state="LOGIN_USERNAME")
async def check_login_username(message: types.Message):
    _ = get_locale(message)
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            _(
                "You already have an account with username {user.user_name} "
                "You can use /help to see available commands"
            ).format(user=user)
        )
        await end_login_dialog(message)
        return
    user_name = message.text.strip() or message.from_user.username
    user = User(
        telegram_id=message.from_user.id,
        user_name=user_name,
    )
    response = await user_routes.create_user(user, api_credentials)
    # if response is success send user message that he is created
    if response.status_code == 201:
        await message.reply(
            _("User {user.user_name} created U can use ... commands").format(
                user=user
            ),
            reply=False,
        )
        await end_login_dialog(message)
    # if response is not ok send message that user already exists
    elif response.status_code == 400:
        await message.reply(
            _("User {user.user_name} already exists").format(user=user),
            reply=False,
        )


@dp.message_handler(state="LOGIN_CODE")
async def check_login_code(message: types.Message):
    _ = get_locale(message)
    user = await crud.find_user_by_telegram_id(message.from_user.id)
    if user:
        await message.answer(
            _(
                "You already have an account with username {user.user_name} "
                "You can use /help to see available commands"
            ).format(user=user)
        )
        await end_login_dialog(message)
        return
    code = message.text.strip()
    try:
        response = await user_routes.redeem_code(
            message.from_user.id,
            code_alias=code,
            credentials=api_credentials,
        )
        if response.status_code == 200:
            await message.reply(
                _("User linked with code {code} U can use ... commands").format(
                    code=code
                ),
                reply=False,
            )
    except HTTPException as e:
        await message.answer(e.detail)
        await end_login_dialog(message)


@dp.callback_query_handler(
    state=["LOGIN_USERNAME", "LOGIN_START"], text="login_end"
)
async def login_end(callback: types.CallbackQuery):
    _ = get_locale(callback)
    await callback.message.answer(_("Login dialog ended"))
    state = dp.current_state(user=callback.from_user.id)
    await state.reset_state()
    await callback.answer()


async def end_login_dialog(message: types.Message):
    _ = get_locale(message)
    await message.reply(_("Login dialog ended"), reply=False)
    state = dp.current_state(user=message.from_user.id)
    await state.reset_state()
