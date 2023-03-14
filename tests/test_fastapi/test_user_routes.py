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
            f"/user/get_user/{semi_random_user.telegram_id}"
        )
        assert (
            response.status_code == 200
        ), f"Failed get request for user {semi_random_user.user_name}"
        assert response.json() == json.loads(
            semi_random_user.json()
        ), f"Failed get data for user {semi_random_user.user_name}"


@pytest.mark.order(99)
@pytest.mark.asyncio
async def test_delete_user(event_loop, semi_random_user: User):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.delete(
            f"/user/delete_user/{semi_random_user.telegram_id}"
        )
        assert response.status_code == 200, "Failed delete user request"
        assert response.json() == {
            "message": "User deleted"
        }, "Failed delete user request"
        assert not await crud.find_user_by_telegram_id(
            semi_random_user.telegram_id
        ), "User was not deleted"
