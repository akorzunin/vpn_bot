import asyncio
import json
import random
import pytest
from httpx import AsyncClient

from src.fastapi_app.fastapi_app import app
from src.db.schemas import User, UserUpdate
from src import PROTECT_DOCS

# mock db
from tests.fixtures.mock_db import replace_db

from tests.fixtures.user_fixtures import (
    test_users,
    event_loop,
    semi_random_user,
    TestUsers,
)
from tests.test_fastapi import api_headers

from src.db import crud

replace_db(crud)


@pytest.mark.asyncio
async def test_docs_access():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/docs")
    if not PROTECT_DOCS:
        assert response.status_code == 200
    else:
        assert response.status_code == 401


@pytest.mark.order(1)
@pytest.mark.asyncio
async def test_create_user(event_loop, semi_random_user: User):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/user/create_user",
            json=json.loads(semi_random_user.json()),
            headers=api_headers,
        )
        assert response.status_code == 201, "Failed create user request"
        assert response.json() == {
            "message": "User created"
        }, "Failed create user request"
        assert await crud.find_user_by_telegram_id(
            semi_random_user.telegram_id
        ), "User was not created"


@pytest.mark.order(2)
@pytest.mark.asyncio
async def test_get_user(event_loop, semi_random_user: User):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            f"/user/get_user/{semi_random_user.telegram_id}",
            headers=api_headers,
        )
        assert (
            response.status_code == 200
        ), f"Failed get request for user {semi_random_user.user_name}"
        assert response.json() == json.loads(
            semi_random_user.json()
        ), f"Failed get data for user {semi_random_user.user_name}"


@pytest.mark.order(3)
@pytest.mark.asyncio
async def test_get_all_users(event_loop):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get(
            "/user/get_all_users",
            headers=api_headers,
        )
        assert response.status_code == 200, "Failed get all users request"


@pytest.mark.order(4)
@pytest.mark.asyncio
async def test_update_user(event_loop, semi_random_user: User):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            f"/user/update_user/{semi_random_user.telegram_id}",
            json=json.loads(semi_random_user.json()),
            headers=api_headers,
        )
        assert response.status_code == 200, "Failed update user request"
        assert response.json() == {
            "message": "User updated"
        }, "Failed update user request"


@pytest.mark.order(5)
@pytest.mark.asyncio
async def test_delete_user(event_loop, semi_random_user: User):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            f"/user/delete_user/{semi_random_user.telegram_id}",
            headers=api_headers,
        )
        assert response.status_code == 200, "Failed delete user request"
        assert response.json() == {
            "message": "User deleted"
        }, "Failed delete user request"
        assert not await crud.find_user_by_telegram_id(
            semi_random_user.telegram_id
        ), "User was not deleted"
