import os
import pytest
from app.managers.databaseManager import DatabaseManager
from app.managers.s3Manager import S3Manager
from fastapi.testclient import TestClient
import pytest_asyncio
from httpx import AsyncClient
from app.schemas.userRoleSchemas import UserRoleCreate
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from app.services.userRoleService import UserRoleService


BASE_URL = "http://localhost:8000"

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
        "email": "test@example.com",
        "pseudo": "testuser",
        "password": "testpassword"   
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        user = response.json()

    yield {"id": user["id"], "pseudo": user["pseudo"], "email": user["email"], "password": "testpassword"}

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        auth_response = await ac.post("/login", data={"username": "testuser", "password": "testpassword"})
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            delete_response = await ac.delete(f"/{user['id']}", headers=headers)

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
    
    yield {"id": user["id"], "pseudo": user["pseudo"], "headers": headers}
    
    await UserRoleService.delete_role(db_session, user["id"])
    
    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        delete_response = await ac.delete(f"/{user['id']}", headers=headers)
        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"


@pytest.fixture()
def s3_mock(mocker):
    mock_s3 = mocker.patch.object(S3Manager, '_instance', None)  # Reset singleton
    return S3Manager()
