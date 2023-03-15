from asyncio import AbstractEventLoop
import pytest
from aiogram import types
from unittest import mock

from tests.fixtures.user_fixtures import event_loop, test_users, TestUsers
from src.aiogram_app import user_commands
from src.db.schemas import User
from src.db import crud


@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_user_command(
    event_loop: AbstractEventLoop, test_users: TestUsers
):
    message = types.Message()
    message.from_user = mock.AsyncMock()
    message.answer = mock.AsyncMock()
    message.from_user.id = test_users.new_user.telegram_id
    await user_commands.t_me(message)
    message.answer.assert_called_once()
    assert (
        "User not found" not in message.answer.await_args[0][0]  # type: ignore
    ), "User not found in message"


@pytest.mark.order(99)
@pytest.mark.asyncio
async def test_delete_user(
    event_loop: AbstractEventLoop, test_users: TestUsers
):
    message = types.Message()
    message.from_user = mock.AsyncMock()
    message.answer = mock.AsyncMock()
    message.from_user.id = test_users.new_user.telegram_id
    await user_commands.delete_user(message)
    assert not await crud.find_user_by_telegram_id(
        message.from_user.id
    ), "User was not deleted"
    message.answer.assert_called_once()
    assert (
        "User not found" not in message.answer.await_args[0][0]  # type: ignore
    ), "User not found in message"


@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_get_balance(
    event_loop: AbstractEventLoop, test_users: TestUsers
):
    message = types.Message()
    message.from_user = mock.AsyncMock()
    message.answer = mock.AsyncMock()
    message.from_user.id = test_users.new_user.telegram_id
    await user_commands.get_balance(message)
    message.answer.assert_called_once()
    assert (
        "Balance" in message.answer.await_args[0][0]  # type: ignore
    ), "Balance not found in message"
    assert (
        "Next payment" in message.answer.await_args[0][0]  # type: ignore
    ), "Next payment not found in message"
