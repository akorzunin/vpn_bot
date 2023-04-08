"""CRUD functions for database operations
    Even if tinydb is not async functions is still coroutines
    in order to migrate to async db connector in future
"""

import contextlib
from datetime import UTC, datetime, timezone
import logging
from uuid import uuid4
from tinydb import Query, where

from src.db.db_conn import users, payments
from src.db.schemas import (
    Money,
    User,
    UserPayment,
    UserUpdate,
    VpnConfig,
    VpnPayment,
    VpnPaymentId,
)
from src.utils.errors.config_errors import ConfigException
from src import MAX_CONFIGS
from src.fastapi_app import pivpn_wrapper as pivpn
from src.utils.errors.db_errors import UserHasNoConfigs
from src.utils.errors.pivpn_errors import UserAlreadyDisabledError


async def find_user_by_telegram_id(telegram_id: int) -> User | None:
    # get one user by id or return None
    if user := users.get(where("telegram_id") == telegram_id):
        return User(**user)
    return None


async def get_user_by_telegram_id(telegram_id: int) -> User:
    # get one user by id
    if user := await find_user_by_telegram_id(telegram_id):
        return user
    raise ValueError("User not found")


async def get_user_by_user_name(username: str) -> User | None:
    # get one user by id
    if user := users.get(where("user_name") == username):
        return User(**user)
    return None


# create user
async def create_user(user) -> None:
    users.insert(user.dict())


# get all users
async def get_all_users():
    return users.all()


async def get_all_enabled_users():
    return users.search(where("is_enabled") == True)


# update user
async def update_user(telegram_id: int, user: UserUpdate) -> None:
    User = Query()
    # filter not None values from user
    user_new_values = {k: v for k, v in user.dict().items() if v is not None}
    # update user

    users.update(
        user_new_values,
        User.telegram_id == telegram_id,
    )


# delete user
async def delete_user(user) -> None:
    User = Query()
    users.remove(User.telegram_id == user.telegram_id)


def add_vpn_config(telegram_id: int, vpn_config: VpnConfig) -> None:
    User = Query()
    # get old vpn configs list from user
    old_vpn_configs = users.get(User.telegram_id == telegram_id)["conf_files"]  # type: ignore
    if old_vpn_configs is None:
        old_vpn_configs = []
    old_vpn_configs.append(vpn_config.dict())
    assert isinstance(old_vpn_configs, list), "old_vpn_configs is not list"
    if len(old_vpn_configs) > MAX_CONFIGS:
        raise ConfigException("Max configs limit is 3")
    # configs w/ same user_nmae are not allowed
    if len({vpn_config["user_name"] for vpn_config in old_vpn_configs}) != len(
        old_vpn_configs
    ):
        raise ConfigException("Config with same user_name already exists")
    users.update(
        {"conf_files": old_vpn_configs},
        User.telegram_id == telegram_id,
    )


def remove_vpn_config(telegram_id: int, vpn_user: str) -> None:
    User = Query()
    # get old vpn configs list from user
    old_vpn_configs: list = users.get(User.telegram_id == telegram_id)[  # type: ignore
        "conf_files"
    ]
    # remove vpn config from list
    vpn_configs = [
        vpn_config
        for vpn_config in old_vpn_configs
        if vpn_config["user_name"] != vpn_user
    ]
    users.update(
        {"conf_files": vpn_configs},
        User.telegram_id == telegram_id,
    )


async def create_user_payment(payment: UserPayment) -> VpnPaymentId:
    """Create payment for user
    add payment to db, and assing payment id to user
    """
    await assingn_payment_to_user(payment)
    # insert payment
    payments.insert(payment.dict())
    return payment.id


async def assingn_payment_to_user(payment: UserPayment) -> None:
    User = Query()
    # get all payments
    user = await get_user_by_telegram_id(payment.user_id)
    if not user:
        raise ValueError("User not found")
    user_payments = user.all_payments
    if user_payments is None:
        user_payments = []
    # add new payment
    user_payments.append(payment.id)
    users.update(
        {
            "all_payments": user_payments,
        },
        User.telegram_id == payment.user_id,
    )


async def create_invoice(user_id: int, amount: Money):
    """Used in billing task to add entry about charge in db"""
    payment_id = VpnPaymentId(uuid4())
    payment = VpnPayment(
        id=payment_id,
        user_id=user_id,
        amount=Money(-abs(amount)),
        date=datetime.now(),
        is_payed=True,
    )

    User = Query()
    # get all payments
    user = users.get(User.telegram_id == user_id)
    if not user:
        raise ValueError("User not found")
    user_payments = user["all_payments"]
    if user_payments is None:
        user_payments = []
    # add new payment
    user_payments.append(payment_id)
    users.update(
        {
            "all_payments": user_payments,
            "balance": user["balance"] - abs(payment.amount),
        },
        User.telegram_id == user_id,
    )
    # insert payment
    payments.insert(payment.dict())


async def update_user_next_payment(
    user_id: int, next_payment: datetime
) -> User:
    users.update(
        {"next_payment": next_payment},
        where("telegram_id") == user_id,
    )
    return await get_user_by_telegram_id(user_id)


async def enable_user(user_id: int) -> User:
    user = await get_user_by_telegram_id(user_id)
    if user:
        enable_all_user_configs(user)
        users.update(
            {
                "is_enabled": True,
                "next_payment": datetime.now(timezone.utc),
            },
            where("telegram_id") == user_id,
        )
        logging.warning(f"User {user_id} enabled")
        return await get_user_by_telegram_id(user_id)
    raise ValueError("User not found")


def enable_all_user_configs(user):
    if not user.conf_files:
        raise UserHasNoConfigs("User has no configs")
    for vpn_config in user.conf_files:
        pivpn.enable_vpn_config(vpn_config)


async def disable_user(user_id: int):
    user = await get_user_by_telegram_id(user_id)
    if user:
        with contextlib.suppress(UserAlreadyDisabledError):
            disable_all_user_configs(user)
        users.update({"is_enabled": False}, where("telegram_id") == user_id)
        logging.warning(f"User {user_id} disabled")


def disable_all_user_configs(user: User):
    if not user.conf_files:
        logging.warning(f"User {user.telegram_id} has no configs")
        return
        # raise ValueError("User has no configs")
    for vpn_config in user.conf_files:
        pivpn.disable_vpn_config(vpn_config)


async def get_paymnet_by_id(payment_id: VpnPaymentId) -> VpnPayment:
    if payment := payments.get(where("id") == payment_id):
        return VpnPayment(**payment)
    raise ValueError("Payment not found")


async def accept_payment(payment: VpnPayment) -> VpnPayment:
    """Mark paymen as confirmed, and add money to user balance"""
    if payment.is_payed:
        raise ValueError("Payment already payed")
    # TODO generalize to another function
    User = Query()
    user = await get_user_by_telegram_id(payment.user_id)
    # TODO update more fields
    users.update(
        {
            "balance": user.balance + payment.amount,
        },
        User.telegram_id == payment.user_id,
    )
    payment.is_payed = True
    payment.date_confirmed = datetime.now(UTC)
    payments.update(
        payment.dict(),
        where("id") == payment.id,
    )
    return payment
