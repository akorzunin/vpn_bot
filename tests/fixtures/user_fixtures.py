import pytest
from src.db.schemas import User, UserUpdate
from src.db import crud

# mock db
from tests.fixtures.mock_db import replace_db

replace_db(crud)


async def upsert_user(user: User) -> User:
    if await crud.find_user_by_telegram_id(user.telegram_id):
        await crud.update_user(user.telegram_id, UserUpdate(**user.dict()))
    else:
        await crud.create_user(user)
    return await crud.get_user_by_telegram_id(user.telegram_id)


@pytest.mark.asyncio
@pytest.fixture(scope="module")
async def test_users():
    # create test users
    new_user = await upsert_user(
        User(
            **{
                "user_name": "test_new_user",
                "telegram_id": 1,
                "is_enabled": False,
            }
        )
    )
    no_balance_enabled_user = await upsert_user(
        User(
            **{
                "user_name": "test_no_balance_enabled_user",
                "telegram_id": 2,
                "is_enabled": True,
            }
        )
    )
    no_balance_disabled_user = await upsert_user(
        User(
            **{
                "user_name": "test_no_balance_disabled_user",
                "telegram_id": 3,
                "is_enabled": False,
            }
        )
    )
    not_zero_balance_enabled_user = await upsert_user(
        User(
            **{
                "user_name": "test_not_zero_balance_enabled_user",
                "telegram_id": 4,
                "is_enabled": True,
                "balance": 100_000,
            }
        )
    )
    not_zero_balance_disabled_user = await upsert_user(
        User(
            **{
                "user_name": "test_not_zero_balance_disabled_user",
                "telegram_id": 5,
                "is_enabled": False,
                "balance": 100_000,
            }
        )
    )

    return dict(
        new_user=new_user,
        no_balance_enabled_user=no_balance_enabled_user,
        no_balance_disabled_user=no_balance_disabled_user,
        not_zero_balance_enabled_user=not_zero_balance_enabled_user,
        not_zero_balance_disabled_user=not_zero_balance_disabled_user,
    )
