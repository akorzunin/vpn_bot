import logging
from datetime import datetime, timedelta, timezone

import src
from src.db import crud
from src.db.schemas import Money, User
from src.tasks.scheduler import scheduler


async def recreate_user_billing_tasks(scheduler=scheduler):
    """Recreate all user billing tasks"""
    logging.info("Recreating user billing tasks")
    # get all users
    users = await crud.get_all_enabled_users()
    if not users:
        logging.info("No users found")
    # recreate all user billing tasks
    for user in users:
        # create billing task
        await create_user_billing_task(User(**user), scheduler)


async def create_user_billing_task(user: User, scheduler=scheduler) -> None:
    """Create user billing task"""
    # create new task
    scheduler.add_job(
        billing_task,
        "date",
        run_date=user.next_payment,
        id=f"billing_{user.telegram_id}",
        args=[user.telegram_id, scheduler],
        replace_existing=True,
    )


def update_job(user: User, scheduler=scheduler):
    """Update user billing task"""
    # get user billing task
    if task := scheduler.get_job(f"billing_{user.telegram_id}"):
        logging.info(
            f"Updating billing task for user {user.telegram_id} to {user.next_payment}"
        )
        task.next_run_time = user.next_payment
        return
    # update user billing task
    scheduler.add_job(
        billing_task,
        "date",
        run_date=user.next_payment,
        id=f"billing_{user.telegram_id}",
        args=[user.telegram_id, scheduler],
    )


async def billing_task(telegram_id: int, scheduler=scheduler) -> None:
    """User billing task"""
    logging.info(f"billing_task for user {telegram_id}")
    # get user
    user = await crud.get_user_by_telegram_id(telegram_id)
    if not user:
        logging.error(f"User not found {telegram_id} terminated billing task")
        raise ValueError("User not found")

    if user.balance < src.PAYMENT_AMOUNT:
        await crud.disable_user(telegram_id)
        return

    if user.is_enabled:
        if user.next_payment:
            await crud.create_invoice(telegram_id, src.PAYMENT_AMOUNT)
            updated_user = await crud.update_user_next_payment(
                user.telegram_id,
                get_next_payment_date(user.next_payment),
            )
            update_job(updated_user, scheduler)
        else:
            # disable user if he is not intended to pay
            await crud.disable_user(telegram_id)


def get_next_payment_date(user_next_payment: datetime) -> datetime:
    """Get next payment date"""
    if (
        user_next_payment
        < datetime.now(timezone.utc) - src.ALLOWED_DOWNTIME_DELAY
    ):
        return datetime.now(timezone.utc) + src.BILL_PERIOD
    return user_next_payment + src.BILL_PERIOD


async def activate_subscription(user_id: int, scheduler=scheduler) -> bool:
    """Activate user subscription"""
    # get user
    user = await crud.get_user_by_telegram_id(user_id)
    if not user:
        logging.error(f"User not found {user_id}")
        return False
    if user.is_enabled and scheduler.get_job(f"billing_{user.telegram_id}"):
        logging.warning(f"User {user.telegram_id} is already enabled")
        # TODO add exception to handle this case
        return False
    # update user
    updated_user = await crud.enable_user(user_id)

    # create billing task
    scheduler.add_job(
        billing_task,
        "date",
        id=f"billing_{updated_user.telegram_id}",
        args=[updated_user.telegram_id, scheduler],
        replace_existing=True,
    )
    return True
