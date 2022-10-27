import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def initial_check_test():
    async with AsyncClient(app=app, base_url="http://127.0.0.1") as ac:
        response = await ac.get("/employees")
    assert response.status_code == 200

