import asyncio
import logging
from datetime import UTC

from apscheduler.events import (
    EVENT_JOB_ERROR,
    EVENT_JOB_EXECUTED,
    EVENT_JOB_MISSED,
    EVENT_JOB_REMOVED,
)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from src import NO_REVIVE_PERIOD
from src.db import crud
from src.loop import loop

scheduler_config = {
    "coalesce": True,  # run job after its missed in down time
    "max_instances": 1,  # run only one instance of job
    "misfire_grace_time": int(
        NO_REVIVE_PERIOD.total_seconds()
    ),  # time to pick up missed job
}

scheduler = AsyncIOScheduler(
    event_loop=loop,
    job_defaults=scheduler_config,
)


def call_coroutine(coro):
    def wrapper(*args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.create_task(coro(*args, **kwargs))

    return wrapper


def get_user_id_from_job_id(job_id: str) -> int:
    return int(job_id.split("_")[1])


def exeption_listener(event):
    if event.exception:
        logging.error(f"{event.exception} The job crashed")


@call_coroutine
async def job_missed_listener(event):
    user_id = get_user_id_from_job_id(event.job_id)
    user = await crud.get_user_by_telegram_id(user_id)
    logging.warning(
        f"Job {event.job_id} {user.balance} {user.next_payment} missed"
    )


@call_coroutine
async def job_removed_listener(event):
    logging.info(f"Removed Job {event.job_id}")


scheduler.add_listener(
    exeption_listener,
    EVENT_JOB_EXECUTED | EVENT_JOB_ERROR,
)

scheduler.add_listener(
    job_missed_listener,
    EVENT_JOB_MISSED,
)

scheduler.add_listener(
    job_removed_listener,
    EVENT_JOB_REMOVED,
)
