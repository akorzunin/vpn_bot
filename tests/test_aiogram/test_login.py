"""Tests for login module"""

import asyncio
import pytest
from unittest import mock
from aiogram import types
import dill
from aiogram.types.inline_keyboard import InlineKeyboardMarkup

from src.aiogram_app import login_commands
from src.aiogram_app.aiogram_app import dp


@pytest.mark.asyncio
async def test_login():
    """Test login"""
    message = types.Message()
    message.from_user = mock.Mock()
    message.answer = mock.AsyncMock()
    message.reply = mock.AsyncMock()
    with open(
        "./tests/mock_data/mock_login/login_inline_buttons.pkl", "rb"
    ) as f:
        keyboard_markup: InlineKeyboardMarkup = dill.load(f)
    await login_commands.login_start(message)
    keyboard_markup.inline_keyboard[0][0].text = "Login with username"
    keyboard_markup.inline_keyboard[1][0].text = "Login with invitation code"
    keyboard_markup.inline_keyboard[2][0].text = "Cancel"
    message.answer.assert_called_once_with(
        "Select a method to login. "
        "If you don't use vpn yet, please use username method",
        reply_markup=keyboard_markup,
    )
    state = dp.current_state(user=message.from_user.id)
    assert await state.get_state() == "LOGIN_START"
