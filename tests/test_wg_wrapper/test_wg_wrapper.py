import pytest
from requests.cookies import RequestsCookieJar
from src.wg_easy_wrapper import wg_wrapper


def test_get_cookies():
    cookies = wg_wrapper.get_cookies()
    assert isinstance(cookies, RequestsCookieJar)


def test_get_all_clients():
    clients = wg_wrapper.get_all_clients()
    assert isinstance(clients, list)


def test_create_client():
    client = wg_wrapper.create_client("test_client")
    assert isinstance(client, dict)
