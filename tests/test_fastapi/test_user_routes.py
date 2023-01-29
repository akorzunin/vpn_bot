import json
import pytest
from httpx import AsyncClient

from src.fastapi_app.fastapi_app import app
from src.db.schemas import User, UserUpdate
from src import PROTECT_DOCS

# mock db
from tests.fixtures.mock_db import replace_db

from tests.fixtures.user_fixtures import test_users

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


@pytest.mark.asyncio
async def test_get_user(test_users):
    test_users_data: dict[str, User] = await test_users
    for usre_label, user in test_users_data.items():
        async with AsyncClient(app=app, base_url="http://test") as ac:
            response = await ac.get(f"/user/get_user/{user.telegram_id}")
            assert (
                response.status_code == 200
            ), f"Failed get request for user{usre_label}"
            assert response.json() == json.loads(
                user.json()
            ), f"Failed get data for user{usre_label}"
