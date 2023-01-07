from typing import Optional
import requests
import os
import re
from PIL import Image, ImageDraw, ImageFont
from inspect import getmembers, isfunction

from pivpn_api import pivpn_app

PIVPN_HOST = os.getenv("PIVPN_HOST", "192.168.1.132:7070")

pivpn_functions = getmembers(pivpn_app, isfunction)

strip_ansi_codes = lambda s: re.sub(
    r"\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?", "", s
)

parse_line = lambda line: re.split(r"\s{2,}", strip_ansi_codes(line))


def parse_col(columns, line):
    if not columns:
        return {"line": line, "error": "No columns defined"}
    return dict(zip(columns, parse_line(line)))


def parse_table(raw_res_text: str) -> dict:
    """parse output as two list of users: enabled and disabled"""
    enabled_users = disabled_users = columns = []
    enabled = header = None
    for line in raw_res_text.splitlines():
        if "::: Clients Summary :::" in line and enabled is None:
            enabled = header = True
            continue
        if line.startswith("::: Disabled clients :::") and enabled:
            enabled = False
            columns = [
                "type",
                "name",
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
    r = requests.request(method, f"http://{host}/{pivpn_func}", params=params)
    # check response status code
    if r.status_code != 200:
        raise ValueError(f"Error in API call: {r.status_code} {r.reason}")
    return r.json()["stdout"]


def add_client(client: str, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "post", "add_client", params={"user_name": client}, host=host
    )
    # parse data
    if not data:
        raise ValueError(f"Failed to create client: {client}")
    success = filename = path = None
    for line in data.splitlines():
        if "Done!" in line:
            success = True
        if "for easytransfer." in line:
            print(line)
            for word in line.split():
                if ".conf" in word:
                    filename = word
                if "/home" in word:
                    path = word
    if not success or not filename or not path:
        raise ValueError(f"Failed to parse client data: {client}")
    return f"{path}/{filename}"


def backup_clients(host: str = PIVPN_HOST) -> str:
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


def disable_client(client: str, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "post", "disable_client", params={"user_name": client}, host=host
    )
    for line in data.splitlines():
        if "::: Successfully disabled" in line:
            break
    else:
        raise ValueError(f"Failed to disable client: {client}")
    return client


def enable_client(client: str, host: str = PIVPN_HOST) -> str:
    data = api_call(
        "post", "enable_client", params={"user_name": client}, host=host
    )
    for line in data.splitlines():
        if "::: Successfully enabled" in line:
            break
    else:
        raise ValueError(f"Failed to enable client: {client}")
    return client


def list_clients(host: str = PIVPN_HOST) -> dict:
    data = api_call("get", "list_clients", host=host)
    return parse_table(data)


def whoami(host: str = PIVPN_HOST) -> str:
    data = api_call("get", "whoami", host=host)
    return data.splitlines()[0]


def get_qr_client(client: int | str, host: str = PIVPN_HOST) -> Image.Image:
    data = api_call("get", "qr_client", params={"user_name": client}, host=host)
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
    font = ImageFont.truetype("cour.ttf", size=12, encoding="unic")
    # fontsize = 12 => width of char -> 7 height of char -> 14
    width, height = (len(qr[0]) - 1) * 7, len(qr) * 14
    img = Image.new("RGB", (width, height), colorBackground)
    d = ImageDraw.Draw(img)
    d.text((0, 0), qr_str, fill=colorText, font=font)

    return img


def get_all_users(host: str = PIVPN_HOST) -> dict:
    raw_res_text = api_call("get", "get_all_clients", host=host)
    return parse_table(raw_res_text)
