import re
from typing import Callable, ItemsView

from src.db.schemas import User, UserPayment, VpnPayment
from src.locales import en, ru, _


def prepare_user_str(user: User | ItemsView, _: Callable = _) -> str:
    """format user in human readable format"""
    if isinstance(user, User):
        if user.conf_files:
            conf_files = "".join(
                [f"    *{file.user_name}*\n" for file in user.conf_files]
            )
        else:
            conf_files = _("  No configuration files\n")
        return _(
            "User data:\n"
            "- *Username*: {user.user_name}\n"
            "- *Telegram ID:* {user.telegram_id}\n"
            "- *Locale:* {user.locale}\n"
            "- *Balance:* {user.balance}\n"
            "- *Last payment:* {user.last_payment}\n"
            "- *Next payment:* {user.last_payment}\n"
            "- *Total payments:* {all_payments}\n"
            "- *Created at:* {user.created_at}\n"
            "- *Is enabled:* {user.is_enabled}\n"
            "- *Configuration files:*\n"
            "{conf_files}"
        ).format(
            user=user,
            conf_files=conf_files,
            all_payments=len(user.all_payments),
        )
    user_str = _("User data:")
    for k, v in user:
        user_str += f"\n  {k}: {v}"
    return user_str


def prepare_all_user_str(data: dict, _: Callable = _) -> str:
    data_str = _("Enabled users:")
    for user in data["enabled_users"]:
        data_str += f"\n+ {prepare_user_str(user.items())}"
    data_str += _("\nDisabled users")
    for user in data["disabled_users"]:
        data_str += f"\n- {prepare_user_str(user.items())}"
    return data_str


def format_vpn_config(vpn_config: str, user_name: str, _: Callable = _) -> str:
    """format vpn config in human readable format"""
    vpn_config_str = f"{_('Vpn config file')} {user_name}.conf:"
    vpn_config_str += f"\n  ```conf\n{vpn_config}\n```\n"
    return vpn_config_str


def format_many_vpn_configs(
    vpn_configs: list[tuple[str, str]],
    _: Callable = _,
) -> str:
    """format vpn config in human readable format"""
    vpn_config_str = _("All user configs:\n")
    for vpn_config, user_name in vpn_configs:
        vpn_config_str += format_vpn_config(vpn_config, user_name)
    return vpn_config_str


def escape_markdown(text: str) -> str:
    """Helper function to escape telegram markup symbols"""
    return text.replace("_", "\\_")


def format_param(param: dict):
    """format param in human readable format"""
    return f"{param['value']} {param['units']}"


def format_speed_test_data(data: dict, _: Callable = _) -> str:
    """format speed test data in human readable format"""
    data_str = _("Speed test data:")
    for k, v in data.items():
        data_str += f"\n  {k} {format_param(v)}"
    return data_str


def format_invoice_created(invoice: UserPayment, _: Callable = _) -> str:
    """format invoice in human readable format"""
    invoice_str = _("Invoice created:")
    for k, v in invoice.dict().items():
        invoice_str += f"\n  {k}: {v}"
    invoice_str += _("\nTo get payment info use /pay_info")
    return invoice_str
