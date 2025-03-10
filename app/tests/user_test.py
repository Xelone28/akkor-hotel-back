import os 
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.schemas.userRoleSchemas import UserRoleCreate
from sqlalchemy.pool import NullPool
from app.services.userRoleService import UserRoleService

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True, poolclass=NullPool)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture()
async def db_session():
    """Create an isolated session to run functional tests."""
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
async def test_admin_user(test_user, db_session: AsyncSession):
    """
    Promote a test user to admin.
    """
    role_data = UserRoleCreate(user_id=test_user["id"], is_admin=True)
    await UserRoleService.assign_role(db_session, role_data)

    # ✅ Authenticate as admin  
    async with AsyncClient(base_url=f"http://localhost:8000/users") as ac:
        auth_response = await ac.post("/login", data={"username": test_user["pseudo"], "password": test_user["password"]})
        assert auth_response.status_code == 200, f"Login failed: {auth_response.text}"
       
        token = auth_response.json()["access_token"]
    
    yield {"id": test_user["id"], "pseudo": test_user["pseudo"], "headers": {"Authorization": f"Bearer {token}"}}
    await UserRoleService.delete_role(db_session, test_user["id"])

@pytest.mark.asyncio
async def test_login_user(test_user):
    """Test to login a valid user"""
    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/login", data={"username": test_user["pseudo"], "password": test_user["password"]})

        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        json_response = response.json()

        assert "access_token" in json_response, f"Missing 'access_token' in response: {json_response}"
        assert json_response["token_type"] == "bearer", f"Expected 'bearer', got {json_response['token_type']}"

@pytest.mark.asyncio
async def test_login_fail():
    """Test to login with wrong credentials"""
    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/login", data={"username": "randomUsername", "password": "randomPassword"})

    assert response.status_code == 401, f"Expected 401, got {response.status_code}, response: {response.text}"

@pytest.mark.asyncio
async def test_delete_protected():
    """Test that the user is supposed to be logged in order to delete its OWN account"""
    user_data = {
        "email": "user.tobedeleted@gmail.com",
        "pseudo": "toBeDeletedUser",
        "password": "testpassword"
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        create_user = await ac.post("/", json=user_data)

        assert create_user.status_code == 201, f"Expected 201, got {create_user.status_code}, response: {create_user.text}"
        user = create_user.json()

        auth_response = await ac.post("/login", data={"username": "toBeDeletedUser", "password": "testpassword"})
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        delete_response = await ac.delete(f"/{user['id']}", headers=headers)

        assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"

@pytest.mark.asyncio
async def test_delete_fail_no_auth(test_user):
    """Test to delete a user without authentication"""
    async with AsyncClient(base_url="http://localhost:8000/users") as ac:

        delete_response = await ac.delete(f"/{test_user['id']}")

    assert delete_response.status_code == 401, f"Expected 401, got {delete_response.status_code}, response: {delete_response.text}"

@pytest.mark.asyncio
async def test_update_user(test_user):
    """Test to update an existing user profile."""
    
    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        auth_response = await ac.post("/login", data={"username": test_user["pseudo"], "password": test_user["password"]})

        assert auth_response.status_code == 200, f"Expected 200, got {auth_response.status_code}, response: {auth_response.text}"
        token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        updated_data = {"email": "updated_email@example.com"}  
        patch_response = await ac.patch(f"/{test_user['id']}", json=updated_data, headers=headers)

        assert patch_response.status_code == 200, f"Expected 200, got {patch_response.status_code}, response: {patch_response.text}"
        updated_user = patch_response.json()

        assert updated_user["id"] == test_user["id"], f"ID mismatch: expected {test_user['id']}, got {updated_user['id']}"
        assert updated_user["email"] == updated_data["email"], f"Email mismatch: expected {updated_data['email']}, got {updated_user['email']}"

@pytest.mark.asyncio
async def test_admin_can_update_user_role(test_admin_user):
    """Ensure only an admin user can modify another user's role. (Interesting case, cannot use test_user because of the test_admin_user scope)"""
    user_data = {
        "email": "coffe@example.com",
        "pseudo": "coffe",
        "password": "testpassword"   
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        user = response.json()

    async with AsyncClient(base_url=f"http://localhost:8000/users") as ac:
        update_response = await ac.patch(f"/{user['id']}", json={"is_admin": True}, headers=test_admin_user["headers"])

        assert update_response.status_code == 200
    async with AsyncClient(base_url=f"http://localhost:8000/user-roles") as ac:
        role_check_response = await ac.get(f"/{user['id']}", headers=test_admin_user["headers"])
        assert role_check_response.status_code == 200
        assert role_check_response.json()["is_admin"] is True

@pytest.mark.asyncio
async def test_non_admin_cannot_update_user_role(test_user):
    """Normal users should not be able to modify admin roles."""
    
    async with AsyncClient(base_url=f"http://localhost:8000/users") as ac:
        
        auth_response = await ac.post(f"/login", data={"username": test_user["pseudo"], "password": test_user["password"]})
        user_token = auth_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {user_token}"}
        
        update_response = await ac.patch(f"/{test_user["id"]}", json={"is_admin": True}, headers=headers)
        assert update_response.status_code == 403