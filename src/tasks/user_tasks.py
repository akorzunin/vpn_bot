from datetime import datetime, timedelta, timezone
import logging

from src.db import crud
from src.db.schemas import Money, User
from src.tasks.scheduler import scheduler
from src.tasks.task_configs import (
    BILL_PERIOD,
    PAYMENT_AMOUNT,
    ALLOWED_DOWNTIME_DELAY,
)


async def recreate_user_billing_tasks():
    """Recreate all user billing tasks"""
    logging.info("Recreating user billing tasks")
    # get all users
    users = await crud.get_all_enabled_users()
    if not users:
        logging.info("No users found")
    # recreate all user billing tasks
    for user in users:
        # create billing task
        await create_user_billing_task(User(**user))


async def create_user_billing_task(user: User) -> None:
    """Create user billing task"""
    # get user billing task
    if task := scheduler.get_job(f"billing_{user.telegram_id}"):
        # remove old task
        scheduler.remove_job(task.id)
    # create new task
    scheduler.add_job(
        billing_task,
        "date",
        run_date=user.next_payment,
        id=f"billing_{user.telegram_id}",
        args=[user.telegram_id],
    )


def update_job(user: User):
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
        args=[user.telegram_id],
    )


async def billing_task(telegram_id: int) -> None:
    """User billing task"""
    logging.info(f"billing_task for user {telegram_id}")
    # get user
    user = await crud.get_user_by_telegram_id(telegram_id)
    if not user:
        logging.error(f"User not found {telegram_id} terminated billing task")
        raise ValueError("User not found")

    if user.balance < PAYMENT_AMOUNT:
        await crud.disable_user(telegram_id)
        return

    if user.is_enabled:
        if user.next_payment:
            await crud.create_invoice(telegram_id, PAYMENT_AMOUNT)
            updated_user = await crud.update_user_next_payment(
                user.telegram_id,
                get_next_payment_date(user.next_payment),
            )
            update_job(updated_user)
        else:
            # disable user if he is not intended to pay
            await crud.disable_user(telegram_id)


def get_next_payment_date(user_next_payment: datetime) -> datetime:
    """Get next payment date"""
    if user_next_payment < datetime.now(timezone.utc) - ALLOWED_DOWNTIME_DELAY:
        return datetime.now(timezone.utc) + BILL_PERIOD
    return user_next_payment + BILL_PERIOD
