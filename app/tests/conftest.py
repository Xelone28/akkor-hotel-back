import os
import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.schemas.userRoleSchemas import UserRoleCreate
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.services.userRoleService import UserRoleService
    

BASE_URL = "http://localhost:8000"
print(f"TEST_DATABASE_URL: {os.getenv('TEST_DATABASE_URL')}")

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True, poolclass=NullPool)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture()
async def db_session():
    """Create an isolated session for each functional test"""
    async with TestingSessionLocal() as session:
        session.begin()
        yield session
        await session.commit()
        await session.close()

@pytest_asyncio.fixture
async def test_user():
    """Create a user and delete it afterward"""
    user_data = {
        "email": "testing@example.com",
        "pseudo": "testinguser",
        "password": "testpassword"   
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        user = response.json()

        auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}

    yield {"id": user["id"], "pseudo": user["pseudo"], "email": user["email"], "password": user_data["password"], "headers": headers}

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        new_auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if new_auth_response.status_code == 200:
            new_token = auth_response.json()["access_token"]
            new_headers = {"Authorization": f"Bearer {new_token}"}

            delete_response = await ac.delete(f"/{user['id']}", headers=new_headers)
            assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"

@pytest_asyncio.fixture
async def test_admin_user(db_session: AsyncSession):
    """
    Promote a test user to admin.
    """
    user_data = {
        "email": "test@greatExample.com",
        "pseudo": "greattestuser",
        "password": "testpassword"   
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        user = response.json()

    role_data = UserRoleCreate(user_id=user["id"], is_admin=True)
    await UserRoleService.assign_role(db_session, role_data)

    async with AsyncClient(base_url=f"http://localhost:8000/users") as ac:
        auth_response = await ac.post("/login", data={"username": user["pseudo"], "password": user_data["password"]})
        assert auth_response.status_code == 200, f"Login failed: {auth_response.text}"
       
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
    
    yield {"id": user["id"], "pseudo": user["pseudo"], "headers": headers, "is_admin": user["is_admin"], "email": user["email"]}
    
    await UserRoleService.delete_role(db_session, user["id"])
    
    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        delete_response = await ac.delete(f"/{user['id']}", headers=headers)
        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"

@pytest_asyncio.fixture
async def test_hotel(test_admin_user):
    """Create a hotel for testing and delete it afterward"""
    hotel_data = {
        "name": "Test Hotel",
        "address": "Test Street, Paris",
        "description": "A sample hotel for testing.",
        "rating": 4.5,
        "breakfast": True
    }

    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        create_response = await ac.post("/", json=hotel_data, headers=test_admin_user["headers"])
        assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}, response: {create_response.text}"
        hotel = create_response.json()

    yield {**hotel, "headers": test_admin_user["headers"]}

    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        delete_response = await ac.delete(f"/{hotel['id']}", headers=test_admin_user["headers"])
        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"

@pytest_asyncio.fixture
async def test_room(test_hotel):
    """Create a room for testing and delete it afterward."""
    room_data = {
        "hotel_id": test_hotel["id"],
        "price": 120.50,
        "number_of_beds": 2
    }

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        create_response = await ac.post("/", json=room_data, headers=test_hotel["headers"])
        assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}, response: {create_response.text}"
        room = create_response.json()

    yield {**room, "headers": test_hotel["headers"]}

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        delete_response = await ac.delete(f"/{room['id']}", headers=test_hotel["headers"])
        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"
