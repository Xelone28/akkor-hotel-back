import pytest
import pytest_asyncio
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

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
