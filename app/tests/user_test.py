import pytest
import pytest_asyncio
from httpx import AsyncClient

@pytest_asyncio.fixture
async def test_user():
    """Create a user and delete it afterward"""
    user_data = {
        "email": "test@example.com",
        "pseudo": "testuser",
        "password": "testpassword"
    }

    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
        response = await ac.post("/", json=user_data)

        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        user = response.json()

    yield {"id": user["id"], "pseudo": user["pseudo"], "email": user["email"], "password": "testpassword"}

    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
        auth_response = await ac.post("/login", data={"username": "testuser", "password": "testpassword"})
        if auth_response.status_code == 200:
            token = auth_response.json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            delete_response = await ac.delete(f"/{user['id']}", headers=headers)

            assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}, response: {delete_response.text}"

@pytest.mark.asyncio
async def test_login_user(test_user):
    """Test to login a valid user"""
    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
        response = await ac.post("/login", data={"username": test_user["pseudo"], "password": test_user["password"]})

        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
        json_response = response.json()

        assert "access_token" in json_response, f"Missing 'access_token' in response: {json_response}"
        assert json_response["token_type"] == "bearer", f"Expected 'bearer', got {json_response['token_type']}"

@pytest.mark.asyncio
async def test_login_fail():
    """Test to login with wrong credentials"""
    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
        response = await ac.post("/login", data={"username": "randomUsername", "password": "randomPassword"})

    assert response.status_code == 401, f"Expected 401, got {response.status_code}, response: {response.text}"
    assert response.json()["detail"] == "Pseudo ou mot de passe invalide", f"Unexpected response: {response.json()}"

@pytest.mark.asyncio
async def test_delete_protected():
    """Test that the user is supposed to be logged in order to delete its OWN account"""
    user_data = {
        "email": "user.tobedeleted@gmail.com",
        "pseudo": "toBeDeletedUser",
        "password": "testpassword"
    }

    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
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
    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
        delete_response = await ac.delete(f"/{test_user['id']}")

    assert delete_response.status_code == 401, f"Expected 401, got {delete_response.status_code}, response: {delete_response.text}"

@pytest.mark.asyncio
async def test_update_user(test_user):
    """Test to update an existing user profile."""
    
    async with AsyncClient(base_url="http://127.0.0.1:8000/users") as ac:
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