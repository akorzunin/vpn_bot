import re
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


def format_vpn_config(vpn_config: str, user_name: str) -> str:
    """format vpn config in human readable format"""
    vpn_config_str = f"Vpn config file {user_name}.conf:"
    vpn_config_str += f"\n  ```conf\n{vpn_config}\n```\n"
    return vpn_config_str


def format_many_vpn_configs(vpn_configs: list[tuple[str, str]]) -> str:
    """format vpn config in human readable format"""
    vpn_config_str = "All user configs:\n"
    for vpn_config, user_name in vpn_configs:
        vpn_config_str += format_vpn_config(vpn_config, user_name)
    return vpn_config_str


def escape_markdown(text: str) -> str:
    """Helper function to escape telegram markup symbols"""
    return text.replace("_", "\\_")


def format_param(param: dict):
    """format param in human readable format"""
    return f"{param['value']} {param['units']}"


def format_speed_test_data(data: dict) -> str:
    """format speed test data in human readable format"""
    data_str = "Speed test data:"
    for k, v in data.items():
        data_str += f"\n  {k} {format_param(v)}"
    return data_str
