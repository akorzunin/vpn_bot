import asyncio
import pytest

import src
from src.tasks.scheduler import scheduler
from tests import mock_globals

src.NO_REVIVE_PERIOD = mock_globals.NO_REVIVE_PERIOD


@pytest.fixture(scope="function")
def mock_scheduler():
    scheduler.start()
    yield scheduler
    scheduler.shutdown()


def test_scheduler(mock_scheduler):
    scheduler = mock_scheduler
    assert scheduler.running
