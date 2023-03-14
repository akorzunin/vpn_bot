import asyncio
from typing import Iterator
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
import uuid

import pytest

import src
from src.db import crud
from src.db.schemas import User, UserUpdate

# mock db
from tests.fixtures.mock_db import replace_db

replace_db(crud)

RANDOM_VPN_CLIENT_NAMES = False


@dataclass
class Name:
    static_name: str = "test_client"
    random_name: str = field(
        default_factory=lambda: f"{str(uuid.uuid4())[:8]}_test_client"
    )


@pytest.fixture(scope="session")
def name():
    return Name()


async def upsert_user(user: User) -> User:
    if await crud.find_user_by_telegram_id(user.telegram_id):
        await crud.update_user(user.telegram_id, UserUpdate(**user.dict()))
    else:
        await crud.create_user(user)
    return await crud.get_user_by_telegram_id(user.telegram_id)


@pytest.fixture(scope="module")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


class TestUsers:
    def __getitem__(self, key):
        return self.__getattribute__(key)

    def __iter__(self) -> Iterator[tuple[str, User]]:
        return iter(self.__dict__.items())

    async def create_users(self):
        user_id = iter(range(1, 100))
        self.new_user = await upsert_user(
            User(
                **{
                    "user_name": "test_new_user",
                    "telegram_id": next(user_id),
                    "is_enabled": False,
                }
            )
        )
        self.no_balance_enabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_no_balance_enabled_user",
                    "telegram_id": next(user_id),
                    "is_enabled": True,
                }
            )
        )
        self.no_balance_disabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_no_balance_disabled_user",
                    "telegram_id": next(user_id),
                    "is_enabled": False,
                }
            )
        )
        self.not_zero_balance_enabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_not_zero_balance_enabled_user",
                    "telegram_id": next(user_id),
                    "is_enabled": True,
                    "balance": 100_000,
                }
            )
        )
        self.not_zero_balance_disabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_not_zero_balance_disabled_user",
                    "telegram_id": next(user_id),
                    "is_enabled": False,
                    "balance": 100_000,
                }
            )
        )
        self.not_zero_balance_enabled_user_w_next_payment = await upsert_user(
            User(
                **{
                    "user_name": "test_not_zero_balance_enabled_user_w_next_payment",
                    "telegram_id": next(user_id),
                    "is_enabled": True,
                    "balance": 100_000,
                    "next_payment": datetime.now(timezone.utc)
                    + src.BILL_PERIOD,
                }
            )
        )
        self.one_paymanet_balance_enabled_user_w_next_payment = await upsert_user(
            User(
                **{
                    "user_name": "test_one_paymanet_balance_enabled_user_w_next_payment",
                    "telegram_id": next(user_id),
                    "is_enabled": True,
                    "balance": src.PAYMENT_AMOUNT,
                    "next_payment": datetime.now(timezone.utc)
                    + src.BILL_PERIOD,
                }
            )
        )
        return self


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def test_users():
    return await TestUsers().create_users()


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def semi_random_user():
    """Returns a user with random name and telegram_id for full test cyccle
    But can be defined stictly for a sengle test case run"""
    return User(
        user_name=Name().random_name
        if RANDOM_VPN_CLIENT_NAMES
        else Name().static_name,
        telegram_id=int("".join(filter(str.isdigit, Name().random_name)))
        if RANDOM_VPN_CLIENT_NAMES
        else 123456,  # telegram id as only digits from random_name
    )
