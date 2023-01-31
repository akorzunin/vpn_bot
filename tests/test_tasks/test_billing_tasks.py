import asyncio
import time
import unittest.mock as mock

import pytest
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import src
from src.db import crud
from src.db.schemas import User
from src.tasks.scheduler import scheduler_config
from src.tasks.user_tasks import recreate_user_billing_tasks
from tests import mock_globals
from tests.fixtures.user_fixtures import test_users

src.NO_REVIVE_PERIOD = mock_globals.NO_REVIVE_PERIOD
from src.logger import logger

# from src.loop import loop

# logging = logger


@pytest.fixture(scope="session")
def scheduler(event_loop):
    scheduler = AsyncIOScheduler(
        event_loop=event_loop,
        # job_defaults=scheduler_config,
    )
    scheduler.start()
    yield scheduler
    scheduler.shutdown()
    # loop.close()


@pytest.fixture(scope="session")
def event_loop():
    return asyncio.new_event_loop()


async def print_pepe(a):
    logger.debug("pawa")
    await a()
    logger.error("pepe")


@pytest.mark.asyncio
async def test_job(
    scheduler,
    test_users,
):
    logger.info(test_users)
    mock_ = mock.AsyncMock()
    scheduler.add_job(print_pepe, "interval", seconds=1, args=[mock_])
    assert scheduler.running
    await asyncio.sleep(1.1)
    mock_.assert_called_once()
