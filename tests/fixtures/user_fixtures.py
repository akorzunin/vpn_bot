import asyncio
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

import pytest

from src.db import crud
from src.db.schemas import User, UserUpdate

# mock db
from tests.fixtures.mock_db import replace_db

replace_db(crud)


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

    async def create_users(self):
        self.new_user = await upsert_user(
            User(
                **{
                    "user_name": "test_new_user",
                    "telegram_id": 1,
                    "is_enabled": False,
                }
            )
        )
        self.no_balance_enabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_no_balance_enabled_user",
                    "telegram_id": 2,
                    "is_enabled": True,
                }
            )
        )
        self.no_balance_disabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_no_balance_disabled_user",
                    "telegram_id": 3,
                    "is_enabled": False,
                }
            )
        )
        self.not_zero_balance_enabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_not_zero_balance_enabled_user",
                    "telegram_id": 4,
                    "is_enabled": True,
                    "balance": 100_000,
                }
            )
        )
        self.not_zero_balance_disabled_user = await upsert_user(
            User(
                **{
                    "user_name": "test_not_zero_balance_disabled_user",
                    "telegram_id": 5,
                    "is_enabled": False,
                    "balance": 100_000,
                }
            )
        )
        self.not_zero_balance_enabled_user_w_next_payment = await upsert_user(
            User(
                **{
                    "user_name": "test_not_zero_balance_enabled_user_w_next_payment",
                    "telegram_id": 6,
                    "is_enabled": True,
                    "balance": 100_000,
                    "next_payment": datetime.now(timezone.utc)
                    + timedelta(seconds=1),
                }
            )
        )
        return self


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def test_users():
    return await TestUsers().create_users()
