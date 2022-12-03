'''CRUD functions for database operations
    Even if tinydb is not async functions is still coroutines
    in order to migrate to async db connector in future
'''
from src.db.db_conn import users
from tinydb import Query


#asunc get user by id
async def get_user_by_telegram_id(telegram_id):
    User = Query()
    return users.search(User.telegram_id == telegram_id)


# create user
async def create_user(user) -> None:
    users.insert(user.dict())

# get all users
async def get_all_users():
    return users.all()
