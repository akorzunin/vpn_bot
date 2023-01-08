import os
from typing import Sequence

from fastapi.security import HTTPBasicCredentials

# TODO handle empty ADMINS env var and convert to ints
admin_users: Sequence[str] = tuple(os.getenv("ADMINS", "").split(", "))


def login_admin(user_id: int):
    if user_id not in admin_users and admin_users:
        raise NotImplementedError("You are not admin")
    return HTTPBasicCredentials(
        username=os.getenv("API_LOGIN", "admin"),
        password=os.getenv("API_PASSWORD", "admin"),
    )
