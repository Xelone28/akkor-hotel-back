import pytest
import pytest_asyncio
from httpx import AsyncClient
from app.schemas.roomSchemas import RoomCreate, RoomUpdate

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_non_admin_cannot_create_room(test_user, test_hotel):
    """Ensure that an unauthorized user cannot create a room."""
    
    room_data = {
        "hotel_id": test_hotel["id"],
        "price": 150.00,
        "number_of_beds": 1
    }

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        response = await ac.post("/", json=room_data, headers=test_user['headers'])
        assert response.status_code == 403, f"Expected 403, got {response.status_code}, response: {response.text}"

@pytest.mark.asyncio
async def test_admin_can_create_room(test_admin_user, test_hotel):
    """An admin should be able to create a room."""
    
    room_data = {
        "hotel_id": test_hotel["id"],
        "price": 150.00,
        "number_of_beds": 1
    }

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        response = await ac.post("/", json=room_data, headers=test_admin_user["headers"])
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"

@pytest.mark.asyncio
async def test_admin_can_update_room(test_admin_user, test_room):
    """An admin should be able to update a room."""
    
    update_data = {
        "price": 200.00,
        "number_of_beds": 3
    }

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        response = await ac.patch(f"/{test_room['id']}", json=update_data, headers=test_admin_user["headers"])
        assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"

@pytest.mark.asyncio
async def test_admin_can_delete_room(test_admin_user, test_hotel):
    """An admin should be able to delete a room."""
    room_data = {
        "hotel_id": test_hotel["id"],
        "price": 120.50,
        "number_of_beds": 2
    }

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        create_response = await ac.post("/", json=room_data, headers=test_hotel["headers"])
        assert create_response.status_code == 201, f"Expected 201, got {create_response.status_code}, response: {create_response.text}"
        room = create_response.json()

    async with AsyncClient(base_url=f"{BASE_URL}/rooms") as ac:
        response = await ac.delete(f"/{room['id']}", headers=test_admin_user["headers"])
        assert response.status_code == 204, f"Expected 204, got {response.status_code}, response: {response.text}"