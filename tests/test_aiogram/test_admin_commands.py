from asyncio import AbstractEventLoop
import pytest
from aiogram import types
from unittest import mock

from tests.fixtures.user_fixtures import event_loop
from src.aiogram_app import admin_commands


@pytest.mark.asyncio
async def test_speed_test(event_loop: AbstractEventLoop):
    message = types.Message()
    message.from_user = mock.Mock()
    message.answer = mock.AsyncMock()
    await admin_commands.speed_test(message)
    message.answer.assert_called_once()
