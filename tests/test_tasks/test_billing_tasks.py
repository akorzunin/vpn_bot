import asyncio
import time
import unittest.mock as mock

import pytest
import src
from apscheduler.schedulers.asyncio import AsyncIOScheduler
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


@pytest.mark.asyncio
async def test_scheduler_jobs(scheduler, test_users):
    scheduler = scheduler
    await recreate_user_billing_tasks()
    jobs = scheduler.get_jobs()
    assert len(jobs) == 2

    while len(jobs) != 0:
        time.sleep(1)
        logger.info("waiting for scheduler to run")


@pytest.mark.asyncio
async def test_regular_payment(capsys, scheduler, test_users):
    # put capsys into test func arg
    with capsys.disabled():

        test_users = await test_users
        scheduler = scheduler
        # get user fron db and save to before_user variable
        before_user: User = test_users["not_zero_balance_enabled_user"]
        await recreate_user_billing_tasks()
        # wait for scheduler to run
        from time import sleep

        sleep(20)
        await asyncio.sleep(mock_globals.BILL_PERIOD.total_seconds() + 1)

        # get user from db and save to after_user variable
        after_user = await crud.get_user_by_telegram_id(before_user.telegram_id)
        # enabled_user_w/_balance -> test_regular_payment -> user.balance == before_user.balance - PAY_AMOUNT
        assert after_user.balance == (
            before_user.balance - mock_globals.PAYMENT_AMOUNT
        ), "job does not affect user balance, user: {user.telegram_id}, test user type: not_zero_balance_enabled_user"
        # next payment should be changed
        assert (
            scheduler.get_job(f"payment_{after_user.telegram_id}").next_run_time
            != scheduler.get_job(
                f"payment_{before_user.telegram_id}"
            ).next_run_time
        ), "job does not change next payment time, user: {user.telegram_id}, test user type: not_zero_balance_enabled_user"


@pytest.mark.asyncio
async def test_not_enough_balance(capsys, scheduler, test_users):
    # from src.tasks import scheduler as scheduler_module

    # scheduler_module.scheduler = scheduler
    with capsys.disabled():
        if not scheduler.running:
            scheduler.start()
        # get user fron db and save to before_user variable
        before_user: User = test_users["no_balance_enabled_user"]
        await recreate_user_billing_tasks(scheduler)
        # wait for scheduler to run
        await asyncio.sleep(mock_globals.BILL_PERIOD.total_seconds() + 1)
        # get user from db and save to after_user variable
        after_user = await crud.get_user_by_telegram_id(before_user.telegram_id)
        # enabled_user_w/_balance -> test_regular_payment -> user.balance == before_user.balance - PAY_AMOUNT
        assert (
            after_user.balance == 0
        ), "job does not affect user balance, user: {user.telegram_id}, test user type: zero_balance_enabled_user"
        # next payment should be changed
        assert (
            scheduler.get_job(f"payment_{after_user.telegram_id}").next_run_time
            != scheduler.get_job(
                f"payment_{before_user.telegram_id}"
            ).next_run_time
        ), "job does not change next payment time, user: {user.telegram_id}, test user type: zero_balance_enabled_user"
