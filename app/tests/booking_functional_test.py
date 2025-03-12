import pytest
from app.services.bookingService import BookingService
from app.schemas.bookingSchemas import BookingCreate, BookingUpdate, BookingResponse
from app.schemas.userSchemas import UserCreate, UserResponse
from app.services.userService import UserService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_create_booking(db_session: AsyncSession, test_user, test_room):
    """Test creating a new booking."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=True
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    assert booking.id is not None
    assert booking.user_id == test_user["id"]
    assert booking.room_id == test_room["id"]
    assert booking.nbr_people == 2
    assert booking.breakfast is True

@pytest.mark.asyncio
async def test_create_booking_invalid_room(db_session: AsyncSession, test_user):
    """Test creating a booking with a non-existent room."""
    booking_data = BookingCreate(
        room_id=9999,
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=True
    )

    with pytest.raises(HTTPException) as exc_info:
        await BookingService.create_booking(db_session, booking_data, test_user)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Room not found"

@pytest.mark.asyncio
async def test_get_booking(db_session: AsyncSession, test_user, test_room):
    """Test retrieving a booking by ID."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=3),
        nbr_people=3,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])

    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    retrieved_booking = await BookingService.get_booking(db_session, booking.id)

    assert retrieved_booking is not None
    assert retrieved_booking.id == booking.id
    assert retrieved_booking.user_id == test_user["id"]
    assert retrieved_booking.room_id == test_room["id"]

@pytest.mark.asyncio
async def test_get_bookings_as_user(db_session: AsyncSession, test_user, test_admin_user, test_room):
    """Test retrieving bookings as a regular user (should only see their own)."""
    booking_data1 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        nbr_people=1,
        breakfast=False
    )

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking1 = await BookingService.create_booking(db_session, booking_data1, userReponse)

    booking_data2 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=True
    )
    adminUserReponse = UserResponse(id=test_admin_user["id"], email=test_admin_user["email"], pseudo=test_admin_user["pseudo"], is_admin=test_admin_user["is_admin"])

    booking2 = await BookingService.create_booking(db_session, booking_data2, adminUserReponse)

    bookings = await BookingService.get_bookings(db_session, userReponse)

    assert len(bookings) == 1
    assert bookings[0].id == booking1.id

@pytest.mark.asyncio
async def test_get_bookings_as_admin(db_session: AsyncSession, test_user, test_admin_user, test_room):
    """Test retrieving all bookings as an admin user."""
    booking_data1 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        nbr_people=1,
        breakfast=False
    )

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking1 = await BookingService.create_booking(db_session, booking_data1, userReponse)

    booking_data2 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=True
    )

    adminUserReponse = UserResponse(id=test_admin_user["id"], email=test_admin_user["email"], pseudo=test_admin_user["pseudo"], is_admin=test_admin_user["is_admin"])
    booking2 = await BookingService.create_booking(db_session, booking_data2, adminUserReponse)

    bookings = await BookingService.get_bookings(db_session, adminUserReponse)

    assert len(bookings) == 2
    assert any(b.id == booking1.id for b in bookings)
    assert any(b.id == booking2.id for b in bookings)

@pytest.mark.asyncio
async def test_update_booking_as_owner(db_session: AsyncSession, test_user, test_room):
    """Test updating a booking as the creator."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])

    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    update_data = BookingUpdate(
        nbr_people=3,
        breakfast=True
    )
    updated_booking = await BookingService.update_booking(db_session, booking.id, update_data, userReponse)

    assert updated_booking is not None
    assert updated_booking.nbr_people == 3
    assert updated_booking.breakfast is True

@pytest.mark.asyncio
async def test_update_booking_as_admin(db_session: AsyncSession, test_user, test_admin_user, test_room):
    """Test updating a booking as an admin."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    update_data = BookingUpdate(
        nbr_people=4,
        breakfast=True
    )
    adminUserReponse = UserResponse(id=test_admin_user["id"], email=test_admin_user["email"], pseudo=test_admin_user["pseudo"], is_admin=test_admin_user["is_admin"])
    updated_booking = await BookingService.update_booking(db_session, booking.id, update_data, adminUserReponse)

    assert updated_booking is not None
    assert updated_booking.nbr_people == 4
    assert updated_booking.breakfast is True

@pytest.mark.asyncio
async def test_update_booking_unauthorized(db_session: AsyncSession, test_user, test_room):
    """Test that a user cannot update someone else's booking."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    another_user = await UserService.create_user(db_session, UserCreate(email="another@example.com", pseudo="another", password="anotherpassword"))
    update_data = BookingUpdate(
        nbr_people=5
    )

    with pytest.raises(HTTPException) as exc_info:
        await BookingService.update_booking(db_session, booking.id, update_data, another_user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to update this booking"

@pytest.mark.asyncio
async def test_delete_booking_as_owner(db_session: AsyncSession, test_user, test_room):
    """Test deleting a booking as the creator."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    result = await BookingService.delete_booking(db_session, booking.id, userReponse)

    assert result is True

    deleted_booking = await BookingService.get_booking(db_session, booking.id)
    assert deleted_booking is None

@pytest.mark.asyncio
async def test_delete_booking_as_admin(db_session: AsyncSession, test_user, test_admin_user, test_room):
    """Test deleting a booking as an admin."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    adminUserReponse = UserResponse(id=test_admin_user["id"], email=test_admin_user["email"], pseudo=test_admin_user["pseudo"], is_admin=test_admin_user["is_admin"])
    result = await BookingService.delete_booking(db_session, booking.id, adminUserReponse)

    assert result is True

    deleted_booking = await BookingService.get_booking(db_session, booking.id)
    assert deleted_booking is None

@pytest.mark.asyncio
async def test_delete_booking_unauthorized(db_session: AsyncSession, test_user, test_room):
    """Test that a user cannot delete someone else's booking."""
    booking_data = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_data, userReponse)

    another_user = await UserService.create_user(db_session, UserCreate(email="another2@example.com", pseudo="another2", password="anotherpassword"))

    with pytest.raises(HTTPException) as exc_info:
        await BookingService.delete_booking(db_session, booking.id, another_user)
    
    assert exc_info.value.status_code == 403
    assert exc_info.value.detail == "Not authorized to delete this booking"

@pytest.mark.asyncio
async def test_get_nonexistent_booking(db_session: AsyncSession):
    """Test retrieving a booking that does not exist."""
    booking = await BookingService.get_booking(db_session, 9999)
    assert booking is None

@pytest.mark.asyncio
async def test_update_nonexistent_booking(db_session: AsyncSession, test_user):
    """Test updating a booking that does not exist."""
    update_data = BookingUpdate(
        nbr_people=3
    )

    with pytest.raises(HTTPException) as exc_info:
        userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
        await BookingService.update_booking(db_session, 9999, update_data, userReponse)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Booking not found"

@pytest.mark.asyncio
async def test_delete_nonexistent_booking(db_session: AsyncSession, test_user):
    """Test deleting a booking that does not exist."""
    with pytest.raises(HTTPException) as exc_info:
        userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
        await BookingService.delete_booking(db_session, 9999, userReponse)
    
    assert exc_info.value.status_code == 404
    assert exc_info.value.detail == "Booking not found"

@pytest.mark.asyncio
async def test_get_bookings_by_user_existing_user(test_user, test_room, db_session):
    """Test that get_bookings_by_user returns correct bookings for an existing user."""
    
    booking_create_1 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=True
    )
    booking_create_2 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today() + timedelta(days=3),
        end_date=date.today() + timedelta(days=5),
        nbr_people=1,
        breakfast=False
    )
    
    user_response = UserResponse(
        id=test_user["id"],
        email=test_user["email"],
        pseudo=test_user["pseudo"]
    )
    
    booking1 = await BookingService.create_booking(db_session, booking_create_1, user_response)
    booking2 = await BookingService.create_booking(db_session, booking_create_2, user_response)    

    bookings = await BookingService.get_bookings_by_user(db_session, test_user["id"])
    
    assert isinstance(bookings, list)
    assert len(bookings) == 2
    assert any(b.id == booking1.id for b in bookings), "Booking1 not found in response"
    assert any(b.id == booking2.id for b in bookings), "Booking2 not found in response"

@pytest.mark.asyncio
async def test_get_bookings_by_user_no_bookings(test_user, db_session):
    """Test that get_bookings_by_user returns an empty list when user has no bookings."""
    
    bookings = await BookingService.get_bookings_by_user(db_session, test_user["id"])
    
    assert isinstance(bookings, list)
    assert len(bookings) == 0, f"Expected 0 bookings, got {len(bookings)}"

@pytest.mark.asyncio
async def test_get_bookings_by_user_nonexistent_user(db_session):
    """Test that get_bookings_by_user returns an empty list for a non-existent user_id."""
    
    non_existent_user_id = 999999
    
    bookings = await BookingService.get_bookings_by_user(db_session, non_existent_user_id)
    
    assert isinstance(bookings, list)
    assert len(bookings) == 0, f"Expected 0 bookings for non-existent user, got {len(bookings)}"