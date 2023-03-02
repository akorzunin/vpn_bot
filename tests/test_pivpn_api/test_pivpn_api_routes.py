import uuid
from dataclasses import dataclass, field
import pytest
import requests

from src import PIVPN_HOST, PIVPN_TOKEN

RANDOM_VPN_CLIENT_NAMES = True

pivpn_headers = {
    "Accept": "application/json",
    "Authorization": f"Basic {PIVPN_TOKEN}",
}


@dataclass
class Name:
    static_name: str = "test_client"
    random_name: str = field(
        default_factory=lambda: f"{str(uuid.uuid4())[:8]}_test_client"
    )


@pytest.fixture(scope="session")
def name():
    return Name()


def get_all_clients():
    return requests.get(
        f"http://{PIVPN_HOST}/get_all_clients",
        headers=pivpn_headers,
    )


# @pytest.mark.dependency(depends=["test_prerun"])
def test_get_all_clients():
    # make request to get all clients
    res = requests.get(
        f"http://{PIVPN_HOST}/get_all_clients",
        headers=pivpn_headers,
    )
    # check response
    assert res.status_code == 200


# TODO @ehsure_not_exist
@pytest.mark.order(1)
def test_add_client(name: Name):
    user_name = (
        name.random_name if RANDOM_VPN_CLIENT_NAMES else name.static_name
    )
    res = requests.post(
        f"http://{PIVPN_HOST}/add_client",
        headers=pivpn_headers,
        params={"user_name": user_name},
    )
    assert res.status_code == 200, f"Error: {res.text}"
    assert (
        r"\n" + user_name + " " in get_all_clients().text
    ), f"User {user_name} not in list"


# TODO @ensure_created
@pytest.mark.order(2)
def test_disable_client(name: Name):
    user_name = (
        name.random_name if RANDOM_VPN_CLIENT_NAMES else name.static_name
    )
    res = requests.post(
        f"http://{PIVPN_HOST}/disable_client",
        headers=pivpn_headers,
        params={"user_name": user_name},
    )
    assert res.status_code == 200
    assert (
        f"Successfully disabled {user_name}" in res.text
        or "already disabled" in res.text
    ), f"Error: {res.text}  {user_name}"
    assert (
        "not exist" not in res.text
    ), f"Error: user {user_name} does not exist"
    assert r"\n" + user_name + " " not in get_all_clients().text


# TODO @ensure_created
@pytest.mark.order(3)
def test_enable_client(name: Name):
    user_name = (
        name.random_name if RANDOM_VPN_CLIENT_NAMES else name.static_name
    )
    res = requests.post(
        f"http://{PIVPN_HOST}/enable_client",
        headers=pivpn_headers,
        params={"user_name": user_name},
    )
    assert res.status_code == 200
    assert (
        "not exist" not in res.text
    ), f"Error: user {user_name} does not exist"
    assert r"\n" + user_name + " " in get_all_clients().text


# TODO @ensure_exist
@pytest.mark.order(4)
def test_delete_client(name: Name):
    user_name = (
        name.random_name if RANDOM_VPN_CLIENT_NAMES else name.static_name
    )
    res = requests.delete(
        f"http://{PIVPN_HOST}/delete_client",
        headers=pivpn_headers,
        params={"user_name": user_name},
    )
    assert res.status_code == 200
    assert (
        "Successfully deleted" in res.text
    ), f"Error: user {user_name} not deleted"
    assert r"\n" + user_name + " " not in get_all_clients().text
