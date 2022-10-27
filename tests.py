import pytest
from httpx import AsyncClient
from main import app, test_engine, override_get_db
from db.config import Base, get_db


@pytest.mark.asyncio
async def test_create_tables():
    app.dependency_overrides[get_db] = override_get_db

    async with test_engine.begin() as conn:  # create tables as first test
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/employees")
        assert response.status_code == 200


@pytest.mark.asyncio
async def test_employee_create():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/employees",
            json={
                "name": "Alexey",
                "age": 35,
                "role": 3,
                "salary": 300000,
                "phone_number": "+78005553535",
            },
        )
        assert response.status_code == 201, response.text
        data = response.json()
        assert data["phone_number"] == "+78005553535"
        assert "id" in data
        employee_id = data["id"]

        response = await ac.get(f"/employees/{employee_id}")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["phone_number"] == "+78005553535"
        assert data["id"] == employee_id


@pytest.mark.asyncio
async def test_employee_read():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/employees/1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["phone_number"] == "+78005553535"
        assert data["id"] == 1


@pytest.mark.asyncio
async def test_employee_full_update():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            f"/employees/1",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 3,
                "salary": 350000,
                "phone_number": "+78005553535",
            },
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["age"] == 36
        assert data["salary"] == 350000
        assert data["phone_number"] == "+78005553535"

        response = await ac.get("/employees/1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["age"] == 36
        assert data["salary"] == 350000
        assert data["phone_number"] == "+78005553535"

        response = await ac.put(
            "/employees/1",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 3,
                "salary": 350000,
            },
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_employee_partial_update():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch(
            "/employees/1",
            json={"role": 1, "phone_number": "+9999999999"},
        )
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["age"] == 36
        assert data["role"] == 1
        assert data["salary"] == 350000
        assert data["phone_number"] == "+9999999999"

        response = await ac.get("/employees/1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert data["age"] == 36
        assert data["role"] == 1
        assert data["salary"] == 350000
        assert data["phone_number"] == "+9999999999"


@pytest.mark.asyncio
async def test_all_employees_read():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/employees",
            json={
                "name": "Mihail",
                "age": 29,
                "role": 2,
                "salary": 150000,
                "phone_number": "+79515555555",
            },
        )
        assert response.status_code == 201
        response = await ac.get("/employees")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 2

        response = await ac.get("/employees?skip=1&limit=100")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1

        response = await ac.get("/employees?skip=0&limit=1")
        assert response.status_code == 200, response.text
        data = response.json()
        assert len(data) == 1


@pytest.mark.asyncio
async def test_try_to_put_not_existing_role():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            "/employees/1",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 0,
                "salary": 350000,
                "phone_number": "+78005553535",
            },
        )
        assert response.status_code == 400, response.text
        assert response.json() == {
            "detail": "Invalid role! Available roles: [1, 2, 3, 4]"
        }


@pytest.mark.asyncio
async def test_try_to_patch_not_existing_role():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch("/employees/1", json={"role": 0})
        assert response.status_code == 400, response.text
        assert response.json() == {
            "detail": "Invalid role! Available roles: [1, 2, 3, 4]"
        }


@pytest.mark.asyncio
async def test_try_to_put_invalid_phone_number():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            f"/employees/1",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 2,
                "salary": 350000,
                "phone_number": "78005553535",
            },
        )
        assert response.status_code == 400, response.text
        assert response.json() == {"detail": "Phone number must contain '+' "}


@pytest.mark.asyncio
async def test_try_to_patch_invalid_phone_number():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch(f"/employees/1", json={"phone_number": "78005553535"})
        assert response.status_code == 400, response.text
        assert response.json() == {"detail": "Phone number must contain '+' "}


@pytest.mark.asyncio
async def test_try_to_put_existing_phone_number():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.put(
            f"/employees/1",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 2,
                "salary": 350000,
                "phone_number": "+79515555555",
            },
        )
        assert response.status_code == 403, response.text
        assert response.json() == {"detail": "Phone number is already registered"}


@pytest.mark.asyncio
async def test_try_to_patch_existing_phone_number():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.patch(
            f"/employees/1", json={"phone_number": "+79515555555"}
        )
        assert response.status_code == 403, response.text
        assert response.json() == {"detail": "Phone number is already registered"}


@pytest.mark.asyncio
async def test_try_to_create_existing_phone_number():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/employees",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 2,
                "salary": 350000,
                "phone_number": "+79515555555",
            },
        )
        assert response.status_code == 403, response.text
        assert response.json() == {"detail": "Phone number is already registered"}


@pytest.mark.asyncio
async def test_try_to_create_invalid_phone_number():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/employees",
            json={
                "name": "Alexey",
                "age": 36,
                "role": 2,
                "salary": 350000,
                "phone_number": "79515555555",
            },
        )
        assert response.status_code == 400, response.text
        assert response.json() == {"detail": "Phone number must contain '+' "}


@pytest.mark.asyncio
async def test_try_to_create_invalid_role():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            f"/employees",
            json={
                "name": "Dmitry",
                "age": 36,
                "role": 0,
                "salary": 350000,
                "phone_number": "+79515525555",
            },
        )
        assert response.status_code == 400, response.text
        assert response.json() == {
            "detail": "Invalid role! Available roles: [1, 2, 3, 4]"
        }


@pytest.mark.asyncio
async def test_drop_tables():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/employees")
        assert response.status_code == 200

    async with test_engine.begin() as conn:  # remove tables as last test
        await conn.run_sync(Base.metadata.drop_all)

    app.dependency_overrides[get_db] = get_db  # setting back main database
