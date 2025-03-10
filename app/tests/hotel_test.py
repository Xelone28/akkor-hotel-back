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

    async with AsyncClient(base_url=f"{BASE_URL}/users") as ac:
        response = await ac.post("/", json=user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        user = response.json()

    yield {"id": user["id"], "pseudo": user["pseudo"], "email": user["email"], "password": "testpassword"}

    async with AsyncClient(base_url=f"{BASE_URL}/users") as ac:
        auth_response = await ac.post("/login", data={"username": "testuser", "password": "testpassword"})
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            delete_response = await ac.delete(f"/{user['id']}", headers=headers)

            assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"
    
@pytest_asyncio.fixture
async def test_admin_user(test_user, db_session: AsyncSession):
    """
    Promote a test user to admin.
    """
    role_data = UserRoleCreate(user_id=test_user["id"], is_admin=True)
    await UserRoleService.assign_role(db_session, role_data)

    # ✅ Authenticate as admin  
    async with AsyncClient(base_url=f"{BASE_URL}/users") as ac:
        auth_response = await ac.post("/login", data={"username": test_user["pseudo"], "password": test_user["password"]})
        assert auth_response.status_code == 200, f"Login failed: {auth_response.text}"
       
        token = auth_response.json()["access_token"]
    
    yield {"id": test_user["id"], "pseudo": test_user["pseudo"], "headers": {"Authorization": f"Bearer {token}"}}

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

@pytest.mark.asyncio
async def test_create_hotel(test_admin_user):
    """Test hotel creation and ownership assignment."""
    hotel_data = {
        "name": "Luxury Paris Hotel",
        "address": "Paris, France",
        "description": "A beautiful hotel in the heart of Paris.",
        "rating": 4.8,
        "breakfast": True
    }
    
    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        create_response = await ac.post("/", json=hotel_data, headers=test_admin_user["headers"])
        assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}, response: {create_response.text}"

        created_hotel = create_response.json()
        assert created_hotel["name"] == "Luxury Paris Hotel"
        assert created_hotel["address"] == "Paris, France"

@pytest.mark.asyncio
async def test_get_hotels():
    """Test retrieving all hotels."""
    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        response = await ac.get("/")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        hotels = response.json()
        assert isinstance(hotels, list)

@pytest.mark.asyncio
async def test_get_hotel_by_id(test_hotel):
    """Test retrieving a hotel by ID."""
    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        response = await ac.get(f"/{test_hotel['id']}")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        hotel = response.json()
        assert hotel["id"] == test_hotel["id"]

@pytest.mark.asyncio
async def test_search_hotels():
    """Test searching for hotels with filters."""
    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        response = await ac.get("/search?name=Luxury")
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        hotels = response.json()
        assert isinstance(hotels, list)

@pytest.mark.asyncio
async def test_update_hotel(test_hotel):
    """Test updating a hotel's details."""
    updated_data = {
        "name": "Updated Test Hotel",
        "address": "Updated Street, Paris"
    }

    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        response = await ac.patch(f"/{test_hotel['id']}", json=updated_data, headers=test_hotel["headers"])
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"

        updated_hotel = response.json()
        assert updated_hotel["name"] == "Updated Test Hotel"
        assert updated_hotel["address"] == "Updated Street, Paris"

@pytest.mark.asyncio
async def test_delete_hotel(test_admin_user):
    """Test that only admins can delete a hotel."""
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
        
    async with AsyncClient(base_url=f"{BASE_URL}/hotels") as ac:
        delete_response = await ac.delete(f"/{hotel['id']}", headers=test_admin_user["headers"])
        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"
