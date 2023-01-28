import pytest
from aiogram import types
import unittest.mock as mock


from src.aiogram_app import baisic_commands


@pytest.mark.asyncio
async def test_send_welcome():
    """Test send_welcome"""
    message = types.Message()
    message.answer = mock.AsyncMock()
    await baisic_commands.send_welcome(message)
    message.answer.assert_called_once_with(
        """
        Bot commands:
        start - initiate bot functions for user
        help - display availble commands
        """
    )
