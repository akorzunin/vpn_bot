import asyncio
import unittest.mock as mock
import pytest

import src
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from src.db import crud
from src.db.schemas import User
from src.tasks.scheduler import scheduler_config
from src.tasks.user_tasks import recreate_user_billing_tasks
from tests import mock_globals
from tests.fixtures.user_fixtures import test_users, TestUsers

src.NO_REVIVE_PERIOD = mock_globals.NO_REVIVE_PERIOD
src.BILL_PERIOD = mock_globals.BILL_PERIOD
src.PAYMENT_AMOUNT = mock_globals.PAYMENT_AMOUNT
src.ALLOWED_DOWNTIME_DELAY = mock_globals.ALLOWED_DOWNTIME_DELAY

from src.logger import logger


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
    scheduler: AsyncIOScheduler,
    test_users: TestUsers,
):
    logger.info(test_users)
    mock_ = mock.AsyncMock()
    scheduler.add_job(
        print_pepe,
        "interval",
        id="test_job",
        seconds=1,
        args=[mock_],
    )
    assert scheduler.running
    await asyncio.sleep(1.1)
    mock_.assert_called_once()
    scheduler.remove_job("test_job")


# TODO enshure users exist in DB
@pytest.mark.asyncio
async def test_scheduler_jobs(scheduler, test_users):
    scheduler = scheduler
    await recreate_user_billing_tasks(scheduler)
    jobs = scheduler.get_jobs()
    assert len(jobs) > 0, "no jobs in scheduler"

    while len(scheduler.get_jobs()) == len(jobs):
        await asyncio.sleep(1)
        logger.info("waiting for scheduler to run")


@pytest.mark.asyncio
async def test_regular_payment(capsys, scheduler, test_users):
    # put capsys into test func arg
    with capsys.disabled():
        # get user fron db and save to before_user variable
        before_user: User = test_users[
            "not_zero_balance_enabled_user_w_next_payment"
        ]
        assert before_user.next_payment is not None, "user has no next payment"
        await recreate_user_billing_tasks(scheduler)
        await asyncio.sleep(src.BILL_PERIOD.total_seconds() + 1)
        # get user from db and save to after_user variable
        after_user = await crud.get_user_by_telegram_id(before_user.telegram_id)
        assert after_user.balance <= (
            before_user.balance - src.PAYMENT_AMOUNT
        ), "job does not affect user balance, user: {user.telegram_id}, test user type: not_zero_balance_enabled_user"
        # next payment should be changed
        assert scheduler.get_job(
            f"billing_{after_user.telegram_id}"
        ).next_run_time == (
            before_user.next_payment + src.BILL_PERIOD
        ), "job does not change next payment time, user: {user.telegram_id}, test user type: not_zero_balance_enabled_user"


@pytest.mark.asyncio
async def test_not_enough_balance(scheduler, test_users):
    # get user fron db and save to before_user variable
    before_user: User = test_users["no_balance_enabled_user"]
    await recreate_user_billing_tasks(scheduler)
    # wait for scheduler to run
    await asyncio.sleep(src.BILL_PERIOD.total_seconds() + 1)
    # get user from db and save to after_user variable
    after_user = await crud.get_user_by_telegram_id(before_user.telegram_id)
    # enabled_user_w/_balance -> test_regular_payment -> user.balance == before_user.balance - PAY_AMOUNT
    assert (
        after_user.balance == 0
    ), f"job does not affect user balance, user: {after_user.telegram_id}, test user type: zero_balance_enabled_user"
    assert (
        before_user.is_enabled is True
    ), f"user is not enabled, user: {after_user.telegram_id}, test user type: zero_balance_enabled_user"
    assert (
        after_user.is_enabled is False
    ), f"user is not disabled, user: {after_user.telegram_id}, test user type: zero_balance_enabled_user"


@pytest.mark.asyncio
async def test_block_user_after_sucseccful_payment(
    scheduler: AsyncIOScheduler, test_users: TestUsers
):
    before_user: User = (
        test_users.one_paymanet_balance_enabled_user_w_next_payment
    )
    await recreate_user_billing_tasks(scheduler)
    # wait for firs successful payment and next have to disable user
    await asyncio.sleep(src.BILL_PERIOD.total_seconds() * 2 + 1)
    after_user = await crud.get_user_by_telegram_id(before_user.telegram_id)
    assert (
        after_user.balance == 0
    ), f"job does not affect user balance, user: {after_user.telegram_id}, test user type: one_paymanet_balance_enabled_user"
    assert before_user.is_enabled is True
    assert after_user.is_enabled is False
