import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.roomSchemas import RoomCreate, RoomUpdate
from app.services.roomService import RoomService
from app.services.hotelService import HotelService
from app.schemas.hotelSchemas import HotelCreate

@pytest_asyncio.fixture()
async def test_hotel(db_session: AsyncSession):
    """Create a test hotel before each test."""
    hotel_data = HotelCreate(
        name="Test Hotel",
        address="Test Street, Paris",
        description="A sample hotel for functional testing.",
        rating=4.5,
        breakfast=True
    )
    hotel = await HotelService.create_hotel(db_session, hotel_data, user_id=1)
    yield hotel
    await HotelService.delete_hotel(db_session, hotel.id)

@pytest_asyncio.fixture()
async def test_room(db_session: AsyncSession, test_hotel):
    """Create a test room before each test."""
    room_data = RoomCreate(
        hotel_id=test_hotel.id,
        price=120.50,
        number_of_beds=2
    )
    room = await RoomService.create_room(db_session, room_data)
    yield room
    await RoomService.delete_room(db_session, room.id)

@pytest.mark.asyncio
async def test_create_room(db_session: AsyncSession, test_hotel):
    """Test creating a room."""
    room_data = RoomCreate(
        hotel_id=test_hotel.id,
        price=150.00,
        number_of_beds=1
    )
    
    room = await RoomService.create_room(db_session, room_data)
    
    assert room.id is not None
    assert room.hotel_id == test_hotel.id
    assert room.price == 150.00
    assert room.number_of_beds == 1

@pytest.mark.asyncio
async def test_get_room(db_session: AsyncSession, test_room):
    """Test retrieving a room by ID."""
    room = await RoomService.get_room(db_session, test_room.id)
    
    assert room is not None
    assert room.id == test_room.id
    assert room.price == test_room.price
    assert room.number_of_beds == test_room.number_of_beds

@pytest.mark.asyncio
async def test_get_rooms_by_hotel(db_session: AsyncSession, test_room):
    """Test retrieving all rooms for a hotel."""
    rooms = await RoomService.get_rooms_by_hotel(db_session, test_room.hotel_id)
    
    assert len(rooms) > 0
    assert any(room.id == test_room.id for room in rooms)

@pytest.mark.asyncio
async def test_update_room(db_session: AsyncSession, test_room):
    """Test updating a room."""
    update_data = RoomUpdate(price=200.00, number_of_beds=3)

    updated_room = await RoomService.update_room(db_session, test_room.id, update_data)
    
    assert updated_room is not None
    assert updated_room.price == 200.00
    assert updated_room.number_of_beds == 3

@pytest.mark.asyncio
async def test_delete_room(db_session: AsyncSession, test_room):
    """Test deleting a room."""
    success = await RoomService.delete_room(db_session, test_room.id)
    assert success is True

    deleted_room = await RoomService.get_room(db_session, test_room.id)
    assert deleted_room is None
