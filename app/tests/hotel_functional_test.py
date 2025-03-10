import os
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.hotelSchemas import HotelCreate, HotelUpdate
from app.schemas.userSchemas import UserCreate
from dotenv import load_dotenv
from app.services.hotelService import HotelService
from app.services.userService import UserService
from app.services.userHotelService import UserHotelService
from sqlalchemy.pool import NullPool

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True, poolclass=NullPool)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Create an isolated session for each test."""
    async with TestingSessionLocal() as session:
        await session.begin()
        yield session
        await session.commit()
        await session.close()


@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    """Create a test user."""
    user_data = UserCreate(
        email="hoteluser@example.com",
        pseudo="hotelowner",
        password="securepassword"
    )
    user = await UserService.create_user(db_session, user_data)
    yield user  # Provide the created user for tests
    success = await UserService.delete_user(db_session, user.id)
    assert success is True


@pytest_asyncio.fixture(scope="function")
async def test_hotel(db_session, test_user):
    """Create a test hotel and assign it to the test user."""
    hotel_data = HotelCreate(
        name="Test Hotel",
        address="Test Street, Paris",
        description="A sample test hotel for functional testing.",
        rating=4.5,
        breakfast=True
    )
    hotel = await HotelService.create_hotel(db_session, hotel_data, test_user.id)
    await db_session.commit()  # 🚀 Ensure the hotel is persisted

    yield hotel  # Provide the created hotel for the tests
    success = await HotelService.delete_hotel(db_session, hotel.id)
    assert success is True


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

    hotel = await HotelService.create_hotel(db_session, hotel_data, test_user.id)

    assert hotel.id is not None
    assert hotel.name == "Hilton Test"
    assert hotel.address == "Paris, France"

    # Verify ownership was assigned
    is_owner = await UserHotelService.is_owner(db_session, test_user.id, hotel.id)
    assert is_owner is True


@pytest.mark.asyncio
async def test_get_hotel(db_session, test_hotel):
    """Ensure we can retrieve a hotel by ID."""
    found_hotel = await HotelService.get_hotel(db_session, test_hotel.id)

    assert found_hotel is not None
    assert found_hotel.id == test_hotel.id
    assert found_hotel.name == test_hotel.name


@pytest.mark.asyncio
async def test_get_hotels(db_session, test_hotel):
    """Ensure we can retrieve all hotels."""
    hotels = await HotelService.get_hotels(db_session)
    print("\nRetrieved hotels:", hotels)  # 🛠 Debugging Line

    assert len(hotels) > 0


@pytest.mark.asyncio
async def test_get_hotels_with_filter(db_session, test_hotel):
    """Ensure filtering by name and address works."""
    hotels_by_name = await HotelService.get_hotels(db_session, name="Test Hotel")
    hotels_by_address = await HotelService.get_hotels(db_session, address="Test Street")

    assert len(hotels_by_name) > 0
    assert hotels_by_name[0].id == test_hotel.id
    
    assert len(hotels_by_address) > 0
    assert any(hotel.id == test_hotel.id for hotel in hotels_by_address)


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

    updated_hotel = await HotelService.update_hotel(db_session, test_hotel.id, update_data)

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

    testing = await HotelService.create_hotel(db_session, hotel_data, test_user.id)
    """Ensure a hotel can be deleted."""
    success = await HotelService.delete_hotel(db_session, testing.id)
    assert success is True
