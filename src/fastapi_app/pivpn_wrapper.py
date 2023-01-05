import requests
import os
import re
from PIL import Image, ImageDraw, ImageFont

PIVPN_HOST = os.getenv("PIVPN_HOST", "192.168.1.132:7070")

strip_ansi_codes = lambda s: re.sub(
    r"\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?", "", s
)
parse_line = lambda line: re.split(r"\s{2,}", strip_ansi_codes(line))


def get_qr_client(client: int | str, host: str = PIVPN_HOST) -> Image.Image:
    r = requests.get(f"http://{host}/qr_client?user_name={client}")
    data = r.json()["stdout"]
    qr = [
        i[3:] + "\n"
        for i in strip_ansi_codes(data).splitlines()
        if i.startswith(";1m")
    ]
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
    r = requests.get(f"http://{host}/get_all_clients")
    raw_res_text = r.json()["stdout"]
    # parse output as two list of users: enabled and disabled
    enabled_users = []
    disabled_users = []
    enabled = None
    header = False
    columns = []
    strip_ansi_codes = lambda s: re.sub(
        r"\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?", "", s
    )
    parse_line = lambda line: re.split(r"\s{2,}", strip_ansi_codes(line))

    def parse_col(columns, line):
        if not columns:
            return {"line": line, "error": "No columns defined"}
        return dict(zip(columns, parse_line(line)))

    for line in raw_res_text.splitlines():
        if "::: Connected Clients List :::" in line and enabled is None:
            enabled = True
            header = True
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
