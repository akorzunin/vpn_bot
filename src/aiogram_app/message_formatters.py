from typing import ItemsView

from src.db.schemas import User


def prepare_user_str(user: User | ItemsView) -> str:
    """format user in human readable format"""
    user_str = "User data:"
    for k, v in user:
        user_str += f"\n  {k}: {v}"
    return user_str


def prepare_all_user_str(data: dict) -> str:
    data_str = "Enabled users:"
    for user in data["enabled_users"]:
        data_str += f"\n+ {prepare_user_str(user.items())}"
    data_str += "\nDisabled users"
    for user in data["disabled_users"]:
        data_str += f"\n- {prepare_user_str(user.items())}"
    return data_str
