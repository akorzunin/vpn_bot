import pytest
from httpx import AsyncClient

from src.fastapi_app.fastapi_app import app
from src import PROTECT_DOCS


@pytest.mark.asyncio
async def test_docs_access():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/docs")
    if not PROTECT_DOCS:
        assert response.status_code == 200
    else:
        assert response.status_code == 401
