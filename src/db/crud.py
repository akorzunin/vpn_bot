"""CRUD functions for database operations
    Even if tinydb is not async functions is still coroutines
    in order to migrate to async db connector in future
"""
from tinydb import Query, where

from src.db.db_conn import users
from src.db.schemas import User


# asunc get user by id
async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    # get one user by id
    if user := users.get(where("telegram_id") == telegram_id):
        return User(**user)

# create user
async def create_user(user) -> None:
    users.insert(user.dict())


# get all users
async def get_all_users():
    return users.all()


# update user
async def update_user(user) -> None:
    User = Query()
    users.update(
        user.dict(),
        User.telegram_id == user.telegram_id,
    )


# delete user
async def delete_user(user) -> None:
    User = Query()
    users.remove(User.telegram_id == user.telegram_id)
