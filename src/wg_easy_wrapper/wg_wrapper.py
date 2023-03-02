import asyncio
import json

import requests
from requests.cookies import RequestsCookieJar
from src import WG_HOST, WG_PASSWORD


def get_cookies() -> RequestsCookieJar:
    raise NotImplementedError

    # payload = {
    #     "password": WG_PASSWORD,
    # }
    # headers = {"Content-Type": "application/json"}

    # response = requests.request(
    #     "POST",
    #     f"http://{WG_HOST}/session",
    #     json=payload,
    #     headers=headers,
    # )
    # if response.status_code == 204:
    #     return response.cookies
    # raise WGWrapperError(
    #     f"Failed to get cookies {response.status_code} {response.text}"
    # )


def get_cookies_decorator(func):
    def wrapper(*args, **kwargs):
        cookies = get_cookies()
        return func(*args, cookies=cookies, **kwargs)

    return wrapper


def get_all_clients(cookies: RequestsCookieJar = get_cookies()) -> dict:
    headers = {"Content-Type": "application/json"}
    response = requests.request(
        "GET",
        f"{WG_HOST}/wireguard/client",
        headers=headers,
        cookies=cookies,
    )
    if response.status_code == 200:
        return response.json()
    raise WGWrapperError(
        f"Failed to get all clients {response.status_code} {response.text}"
    )


def create_client(
    name: str, cookies: RequestsCookieJar = get_cookies()
) -> dict:
    headers = {"Content-Type": "application/json"}
    response = requests.request(
        "POST",
        f"{WG_HOST}/wireguard/client",
        headers=headers,
        cookies=cookies,
        data=json.dumps(dict(name=name)),
    )
    if response.status_code == 200:
        return response.json()
    raise WGWrapperError(
        f"Failed to get client {response.status_code} {response.text}"
    )


class WGWrapperError(Exception):
    ...
