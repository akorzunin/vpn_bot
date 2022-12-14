"""CRUD functions for database operations
    Even if tinydb is not async functions is still coroutines
    in order to migrate to async db connector in future
"""
from tinydb import Query, where

from src.db.db_conn import users
from src.db.schemas import User, UserUpdate, VpnConfig
from src.utils.errors.config_errors import ConfigException


# asunc get user by id
async def get_user_by_telegram_id(telegram_id: int) -> User | None:
    # get one user by id
    if user := users.get(where("telegram_id") == telegram_id):  # type: ignore
        return User(**user)
    return None


# create user
async def create_user(user) -> None:
    users.insert(user.dict())


# get all users
async def get_all_users():
    return users.all()


# update user
async def update_user(telegram_id: int, user: UserUpdate) -> None:
    User = Query()
    # filter not None values from user
    user_new_values = {k: v for k, v in user.dict().items() if v is not None}
    # update user

    users.update(
        user_new_values,
        User.telegram_id == telegram_id,  # type: ignore
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
    # max configs limit is 3
    if len(old_vpn_configs) > 3:
        raise ConfigException("Max configs limit is 3")
    # configs w/ same user_nmae are not allowed
    if len({vpn_config["user_name"] for vpn_config in old_vpn_configs}) != len(
        old_vpn_configs
    ):
        raise ConfigException("Config with same user_name already exists")
    users.update(
        {"conf_files": old_vpn_configs},
        User.telegram_id == telegram_id,  # type: ignore
    )


def remove_vpn_config(telegram_id: int, vpn_user: str) -> None:
    User = Query()
    # get old vpn configs list from user
    old_vpn_configs: list = users.get(User.telegram_id == telegram_id)["conf_files"]  # type: ignore
    # remove vpn config from list
    vpn_configs = [
        vpn_config
        for vpn_config in old_vpn_configs
        if vpn_config["user_name"] != vpn_user
    ]
    users.update(
        {"conf_files": vpn_configs},
        User.telegram_id == telegram_id,  # type: ignore
    )
