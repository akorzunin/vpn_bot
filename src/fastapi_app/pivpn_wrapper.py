from typing import Literal, Optional
import requests
import os
import re
from PIL import Image, ImageDraw, ImageFont
from inspect import getmembers, isfunction

from pivpn_api import pivpn_app
from src.db.schemas import VpnConfig
from src.utils.errors.pivpn_errors import (
    UserAlreadyDisabledError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from src import PIVPN_HOST, PIVPN_TOKEN

pivpn_headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {PIVPN_TOKEN}",
}


def check_pivpn_connection() -> bool:
    """check connection to pivpn"""
    try:
        res = requests.get(
            f"http://{PIVPN_HOST}/whoami",
            headers=pivpn_headers,
        )
        return res.status_code == 200 and res.text == '{"stdout":"root\\n"}'
    except Exception as e:
        return False


pivpn_functions = getmembers(pivpn_app, isfunction)

strip_ansi_codes = lambda s: re.sub(
    r"\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?", "", s
)

parse_line = lambda line: re.split(r"\s{2,}", strip_ansi_codes(line))


def parse_col(columns, line):
    return (
        dict(zip(columns, parse_line(line)))
        if columns
        else {"line": line, "error": "No columns defined"}
    )


def parse_table(
    raw_res_text: str,
    enabled_dilimiter: str = "::: Clients Summary :::",
    disabled_dilimiter: str = "::: Disabled clients :::",
) -> dict:
    """parse output as two list of users: enabled and disabled"""
    enabled_users, disabled_users, columns = [], [], []
    enabled = header = None
    for line in raw_res_text.splitlines():
        if enabled_dilimiter in line and enabled is None:
            enabled = header = True
            continue
        if line.startswith(disabled_dilimiter) and enabled:
            enabled = False
            columns = [
                "Type",
                "Name",
            ]
            continue
        if enabled is True:
            if header:
                header = False
                columns = parse_line(line)
                continue
            enabled_users.append(parse_col(columns, line))
        if enabled is False:
            disabled_users.append(parse_col(columns, line))
    return dict(enabled_users=enabled_users, disabled_users=disabled_users)


def api_call(
    method: str,
    pivpn_func: str,
    params: Optional[dict] = None,
    host: str = PIVPN_HOST,
) -> str:
    if params is None:
        params = {}
    # check if function exists in pivpn_functions
    if pivpn_func not in [i[0] for i in pivpn_functions]:
        raise ValueError(f"Function {pivpn_func} not found in pivpn_api")
    r = requests.request(
        method,
        f"http://{host}/{pivpn_func}",
        params=params,
        headers=pivpn_headers,
    )
    # check response status code
    if r.status_code != 200:
        raise ValueError(f"Error in API call: {r.status_code} {r.reason}")
    return r.json()["stdout"]


def add_vpn_config(vpn_config_name: str, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "post", "add_client", params={"user_name": vpn_config_name}, host=host
    )
    # parse data
    if not data or "already exists" in data:
        raise UserAlreadyExistsError(
            f"vpn_config already exists: {vpn_config_name}"
        )
    if "Name can only contain alphanumeric characters" in data:
        raise ValueError(
            "Name can only contain alphanumeric characters and these symbols (.-@_)."
        )
    success = filename = path = None
    for line in data.splitlines():
        if "Done!" in line:
            success = True
        if "for easytransfer." in line:
            for word in line.split():
                if ".conf" in word:
                    filename = word
                if "/home" in word:
                    path = word
    if not success or not filename or not path:
        raise ValueError(f"Failed to parse vpn_config data: {vpn_config_name}")
    return f"{path}/{filename}"


def backup_vpn_configs(host: str = PIVPN_HOST) -> str:
    data = api_call("post", "backup_clients", host=host)
    path = None
    for line in data.splitlines():
        if "/home" in line:
            for word in line.split():
                if "/home" in word:
                    path = word
    if not path:
        raise ValueError(f"Failed to parse backup path: {data}")
    return path


def disable_vpn_config(vpn_config: VpnConfig, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "post",
        "disable_client",
        params={"user_name": vpn_config.user_name},
        host=host,
    )
    for line in data.splitlines():
        if "::: Successfully disabled" in line:
            break
    else:
        if "not exist" in data:
            raise UserNotFoundError(f"vpn_config does not exist: {vpn_config}")
        if "already disabled" in data:
            raise UserAlreadyDisabledError(
                f"vpn_config already disabled: {vpn_config}"
            )
        raise ValueError(f"Failed to disable vpn_config: {vpn_config}")
    return vpn_config.user_name


def enable_vpn_config(vpn_config: str, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "post", "enable_client", params={"user_name": vpn_config}, host=host
    )
    for line in data.splitlines():
        if "::: Successfully enabled" in line:
            break
    else:
        if "not exist" in data:
            raise UserNotFoundError(f"vpn_config does not exist: {vpn_config}")
        if "already disabled" in data:
            raise UserAlreadyDisabledError(
                f"vpn_config already disabled: {vpn_config}"
            )
        raise ValueError(f"Failed to enable vpn_config: {vpn_config}")
    return vpn_config


def delete_vpn_config(vpn_config: str, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "delete", "delete_client", params={"user_name": vpn_config}, host=host
    )
    for line in data.splitlines():
        if "::: Successfully deleted" in line:
            break
    else:
        if "not exist" in data:
            raise UserNotFoundError(f"vpn_config does not exist: {vpn_config}")
        raise ValueError(f"Failed to remove vpn_config: {vpn_config}")
    return vpn_config


def list_vpn_configs(host: str = PIVPN_HOST) -> dict:
    data = api_call("get", "list_clients", host=host)
    return parse_table(data)


def whoami(host: str = PIVPN_HOST) -> str:
    data = api_call("get", "whoami", host=host)
    return data.splitlines()[0]


def get_vpn_config_qr(
    vpn_config: int | str, host: str = PIVPN_HOST
) -> Image.Image:
    data = api_call(
        "get", "qr_client", params={"user_name": vpn_config}, host=host
    )
    # parse response
    qr = [
        i[3:] + "\n"
        for i in strip_ansi_codes(data).splitlines()
        if i.startswith(";1m")
    ]
    if not qr:
        raise ValueError(f"Failed to parse qr from response: {data}")
    qr_str = "".join(qr)
    colorText = "white"
    colorBackground = "black"
    font = ImageFont.truetype("DejaVuSansMono.ttf", size=18, encoding="unic")
    # 10.8, 20.5 are imperical values
    width, height = (len(qr[0]) - 1) * 10.8, len(qr) * 20.5
    img = Image.new("RGB", (int(width), int(height)), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((0, 0), qr_str, fill=colorText, font=font)

    return img


def get_all_users(host: str = PIVPN_HOST) -> dict:
    raw_res_text = api_call("get", "get_all_clients", host=host)
    return parse_table(
        raw_res_text,
        enabled_dilimiter="::: Connected Clients List :::",
        disabled_dilimiter="::: Disabled clients :::",
    )


def get_speed_test(
    type: Literal["full", ""] = "", host: str = PIVPN_HOST
) -> dict:
    data = api_call("get", "speed_test", params={"type": ""}, host=host)
    speed_data: dict[str, str | dict[str, str]] = {}
    if "speedtest-cli" in data:
        raise ValueError(f"Speedtest-cli not installed on {host}")
    if type:
        for line in data.splitlines():
            if "Mbit/s" in line:
                name, value, units = line.split()
                speed_data[name] = {"value": value, "units": units}
        speed_data["raw_text"] = data
    else:
        # parse data output for --simple flag
        for line in data.splitlines():
            if any(x in line for x in ["Ping:", "Download:", "Upload:"]):
                name, value, units = line.split()
                speed_data[name] = {"value": value, "units": units}
    return speed_data


def get_config_by_filepath(filepath: str) -> str:
    """Get config data from file path"""
    data = api_call(
        "get", "get_config_by_filepath", params={"filepath": filepath}
    )
    if not data.startswith("[Interface]"):
        raise ValueError("Invalid config file")
    return data
