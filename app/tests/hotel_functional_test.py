import pytest
from app.schemas.hotelSchemas import HotelCreate, HotelUpdate
from app.services.hotelService import HotelService

@pytest.mark.asyncio
async def test_create_hotel(db_session, test_user):
    """Test hotel creation and ownership assignment."""
    hotel_data = HotelCreate(
        name="Hilton Test",
        address="Paris, France",
        description="A test Hilton hotel.",
        rating=4.8,
        breakfast=True
    )

    hotel = await HotelService.create_hotel(db_session, hotel_data, test_user["id"])

    assert hotel.id is not None
    assert hotel.name == "Hilton Test"
    assert hotel.address == "Paris, France"

@pytest.mark.asyncio
async def test_get_hotel(db_session, test_hotel):
    """Ensure we can retrieve a hotel by ID."""
    found_hotel = await HotelService.get_hotel(db_session, test_hotel["id"])

    assert found_hotel is not None
    assert found_hotel.id == test_hotel["id"]
    assert found_hotel.name == test_hotel["name"]


@pytest.mark.asyncio
async def test_get_hotels(db_session):
    """Ensure we can retrieve all hotels."""
    hotels = await HotelService.get_hotels(db_session)
    assert len(hotels) > 0


@pytest.mark.asyncio
async def test_get_hotels_with_filter(db_session, test_hotel):
    """Ensure filtering by name and address works."""
    hotels_by_name = await HotelService.get_hotels(db_session, name="Test Hotel")
    hotels_by_address = await HotelService.get_hotels(db_session, address="Test Street")

    assert len(hotels_by_name) > 0
    assert hotels_by_name[0].id == test_hotel["id"]
    
    assert len(hotels_by_address) > 0
    assert any(hotel.id == test_hotel["id"] for hotel in hotels_by_address)


@pytest.mark.asyncio
async def test_pagination(db_session):
    """Ensure pagination functionality works."""
    hotels_page_1 = await HotelService.get_hotels(db_session, limit=2, offset=0)
    hotels_page_2 = await HotelService.get_hotels(db_session, limit=2, offset=2)

    assert len(hotels_page_1) == 2
    assert len(hotels_page_2) == 2


@pytest.mark.asyncio
async def test_update_hotel(db_session, test_hotel):
    """Ensure hotel details can be updated properly."""
    update_data = HotelUpdate(
        name="Updated Test Hotel",
        address="Updated Street, Paris"
    )

    updated_hotel = await HotelService.update_hotel(db_session, test_hotel["id"], update_data)

    assert updated_hotel is not None
    assert updated_hotel.name == "Updated Test Hotel"
    assert updated_hotel.address == "Updated Street, Paris"


@pytest.mark.asyncio
async def test_delete_hotel(db_session, test_user):
    hotel_data = HotelCreate(
        name="Hilton Test",
        address="Paris, France",
        description="A test Hilton hotel.",
        rating=4.8,
        breakfast=True
    )

    newHotel = await HotelService.create_hotel(db_session, hotel_data, test_user["id"])

    success = await HotelService.delete_hotel(db_session, newHotel.id)
    assert success is True
