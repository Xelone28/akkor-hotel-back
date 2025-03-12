import pytest
from httpx import AsyncClient
from datetime import date, timedelta
from app.schemas.userSchemas import UserResponse
from app.schemas.bookingSchemas import BookingCreate
from app.services.bookingService import BookingService

BASE_URL = "http://localhost:8000"

@pytest.mark.asyncio
async def test_create_booking_success(test_user, test_room):
    """Test that an authenticated user can create a booking successfully."""
    booking_data = {
        "room_id": test_room["id"],
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=2)),
        "nbr_people": 2,
        "breakfast": True
    }

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/bookings/", json=booking_data, headers=test_user["headers"])

    assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
    json_response = response.json()
    assert json_response["room_id"] == booking_data["room_id"]
    assert json_response["user_id"] == test_user["id"]
    assert json_response["nbr_people"] == booking_data["nbr_people"]
    assert json_response["breakfast"] == booking_data["breakfast"]

@pytest.mark.asyncio
async def test_create_booking_nonexistent_room(test_user):
    """Test that creating a booking with a non-existent room fails."""
    booking_data = {
        "room_id": 999999,
        "start_date": str(date.today()),
        "end_date": str(date.today() + timedelta(days=2)),
        "nbr_people": 2,
        "breakfast": False
    }

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/bookings/", json=booking_data, headers=test_user["headers"])

    assert response.status_code == 404, f"Expected 404, got {response.status_code}, response: {response.text}"
    assert response.json()["detail"] == "Room not found"

@pytest.mark.asyncio
async def test_create_booking_missing_fields(test_user, test_room):
    """Test that creating a booking with missing required fields fails."""
    booking_data = {
        "room_id": test_room["id"],
        "end_date": str(date.today() + timedelta(days=2)),
        "nbr_people": 2
    }

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.post("/bookings/", json=booking_data, headers=test_user["headers"])

    assert response.status_code == 422, f"Expected 422, got {response.status_code}, response: {response.text}"

@pytest.mark.asyncio
async def test_get_booking_success_owner(test_user, test_room, db_session):
    """Test that the booking owner can retrieve their booking."""
    booking_create = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=3),
        nbr_people=1,
        breakfast=False
    )

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create, userReponse)

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get(f"/bookings/{booking.id}", headers=test_user["headers"])

    assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
    json_response = response.json()
    assert json_response["id"] == booking.id
    assert json_response["user_id"] == test_user["id"]

@pytest.mark.asyncio
async def test_get_booking_success_admin(test_admin_user, test_user, test_room, db_session):
    """Test that an admin can retrieve any booking."""
    from app.services.bookingService import BookingService
    from app.schemas.bookingSchemas import BookingCreate

    booking_create = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=3),
        nbr_people=3,
        breakfast=True
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create, userReponse)

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get(f"/bookings/{booking.id}", headers=test_admin_user["headers"])

    assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
    json_response = response.json()
    assert json_response["id"] == booking.id
    assert json_response["user_id"] == test_user["id"]

@pytest.mark.asyncio
async def test_get_booking_not_found(test_user):
    """Test that retrieving a non-existent booking returns 404."""
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get("/bookings/999999", headers=test_user["headers"])

    assert response.status_code == 404, f"Expected 404, got {response.status_code}, response: {response.text}"
    assert response.json()["detail"] == "Booking not found"

@pytest.mark.asyncio
async def test_get_booking_unauthorized(test_user, db_session, test_room):
    """Test that a user cannot retrieve another user's booking."""
    from app.services.bookingService import BookingService
    from app.schemas.bookingSchemas import BookingCreate

    booking_create = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        nbr_people=1,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create, userReponse)

    user_data = {
        "email": "other@example.com",
        "pseudo": "otheruser",
        "password": "otherpassword"
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        other_user = response.json()

        auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if auth_response.status_code == 200:
            other_token = auth_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}

    try:
        async with AsyncClient(base_url=BASE_URL) as ac:
            response = await ac.get(f"/bookings/{booking.id}", headers=other_headers)

        assert response.status_code == 403, f"Expected 403, got {response.status_code}, response: {response.text}"

    finally:
        async with AsyncClient(base_url=BASE_URL) as ac:
            delete_response = await ac.delete(f"/users/{other_user['id']}", headers=other_headers)
            assert delete_response.status_code == 204
        

@pytest.mark.asyncio
async def test_get_all_bookings_admin(test_admin_user, test_user, test_room, db_session):
    """Test that an admin can retrieve all bookings."""
    from app.services.bookingService import BookingService
    from app.schemas.bookingSchemas import BookingCreate

    booking_create_1 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        nbr_people=2,
        breakfast=True
    )
    booking_create_2 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today() + timedelta(days=2),
        end_date=date.today() + timedelta(days=3),
        nbr_people=1,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])

    booking1 = await BookingService.create_booking(db_session, booking_create_1, userReponse)
    booking2 = await BookingService.create_booking(db_session, booking_create_2, userReponse)

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get("/bookings/", headers=test_admin_user["headers"])

    assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
    bookings = response.json()
    assert isinstance(bookings, list)
    assert any(b["id"] == booking1.id for b in bookings)
    assert any(b["id"] == booking2.id for b in bookings)

@pytest.mark.asyncio
async def test_get_all_bookings_user(test_user, test_room, db_session):
    """Test that a user can retrieve only their own bookings."""

    booking_create_1 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=1),
        nbr_people=2,
        breakfast=True
    )
    booking_create_2 = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today() + timedelta(days=2),
        end_date=date.today() + timedelta(days=3),
        nbr_people=1,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])

    booking1 = await BookingService.create_booking(db_session, booking_create_1, userReponse)
    booking2 = await BookingService.create_booking(db_session, booking_create_2, userReponse)

    user_data = {
      "email": "another_example@example.com",
        "pseudo": "another_example",
        "password": "anotherpassword"
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        other_user = response.json()

        auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if auth_response.status_code == 200:
            other_token = auth_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}

    try:
        booking_create_other = BookingCreate(
            room_id=test_room["id"],
            start_date=date.today(),
            end_date=date.today() + timedelta(days=1),
            nbr_people=1,
            breakfast=False
        )
        otherUserReponse = UserResponse(id=other_user["id"], email=other_user["email"], pseudo=other_user["pseudo"])
        booking_other = await BookingService.create_booking(db_session, booking_create_other, otherUserReponse)

        async with AsyncClient(base_url=BASE_URL) as ac:
            response = await ac.get("/bookings/", headers=test_user["headers"])

        assert response.status_code == 200
        bookings = response.json()
        assert isinstance(bookings, list)
        assert any(b["id"] == booking1.id for b in bookings)
        assert any(b["id"] == booking2.id for b in bookings)
        assert not any(b["id"] == booking_other.id for b in bookings)
    finally:
        async with AsyncClient(base_url=BASE_URL) as ac:
            delete_response = await ac.delete(f"/users/{other_user['id']}", headers=other_headers)
            assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_update_booking_success_owner(test_user, test_room, db_session):
    """Test that the booking owner can update their booking."""
    from app.services.bookingService import BookingService
    from app.schemas.bookingSchemas import BookingCreate, BookingUpdate

    booking_create = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create, userReponse)

    update_data = {
        "nbr_people": 3,
        "breakfast": True
    }

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.patch(f"/bookings/{booking.id}", json=update_data, headers=test_user["headers"])

    assert response.status_code == 200, f"Expected 200, got {response.status_code}, response: {response.text}"
    json_response = response.json()
    assert json_response["nbr_people"] == update_data["nbr_people"]
    assert json_response["breakfast"] == update_data["breakfast"]

@pytest.mark.asyncio
async def test_update_booking_success_admin(test_admin_user, test_user, test_room, db_session):
    """Test that an admin can update any booking."""
    from app.services.bookingService import BookingService
    from app.schemas.bookingSchemas import BookingCreate, BookingUpdate

    booking_create = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create, userReponse)

    update_data = {
        "nbr_people": 4,
        "breakfast": True
    }

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.patch(f"/bookings/{booking.id}", json=update_data, headers=test_admin_user["headers"])

    assert response.status_code == 200
    json_response = response.json()
    assert json_response["nbr_people"] == update_data["nbr_people"]
    assert json_response["breakfast"] == update_data["breakfast"]

@pytest.mark.asyncio
async def test_update_booking_unauthorized(test_user, test_room, db_session):
    """Test that a user cannot update another user's booking."""
    from app.services.bookingService import BookingService
    from app.schemas.bookingSchemas import BookingCreate, BookingUpdate

    booking_create = BookingCreate(
        room_id=test_room["id"],
        start_date=date.today(),
        end_date=date.today() + timedelta(days=2),
        nbr_people=2,
        breakfast=False
    )
    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create, userReponse)

    user_data = {
        "email": "updatefail@example.com",
        "pseudo": "updatefailuser",
        "password": "updatepassword"
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        other_user = response.json()

        auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if auth_response.status_code == 200:
            other_token = auth_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}

    try:
        update_data = {
            "nbr_people": 5
        }
        async with AsyncClient(base_url=BASE_URL) as ac:
            response = await ac.patch(f"/bookings/{booking.id}", json=update_data, headers=other_headers)

        assert response.status_code == 403, f"Expected 403, got {response.status_code}, response: {response.text}"
        assert response.json()["detail"] == "Not authorized to update this booking"
    finally:
        async with AsyncClient(base_url=BASE_URL) as ac:
            delete_response = await ac.delete(f"/users/{other_user['id']}", headers=other_headers)
            assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_update_booking_not_found(test_user):
    """Test that updating a non-existent booking returns 404."""

    update_data = {
        "nbr_people": 3
    }

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.patch("/bookings/999999", json=update_data, headers=test_user["headers"])

    assert response.status_code == 404, f"Expected 404, got {response.status_code}, response: {response.text}"
    assert response.json()["detail"] == "Booking not found"

@pytest.mark.asyncio
async def test_delete_booking_success_owner(test_user, test_room, db_session):
    """Test that the booking owner can delete their booking."""
    from app.services.bookingService import BookingService

    booking_create = {
        "room_id": test_room["id"],
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=2),
        "nbr_people": 2,
        "breakfast": False
    }
    from app.schemas.bookingSchemas import BookingCreate
    booking_create_pydantic = BookingCreate(**booking_create)

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create_pydantic, userReponse)

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.delete(f"/bookings/{booking.id}", headers=test_user["headers"])

    assert response.status_code == 204, f"Expected 204, got {response.status_code}, response: {response.text}"

    async with AsyncClient(base_url=BASE_URL) as ac:
        get_response = await ac.get(f"/bookings/{booking.id}", headers=test_user["headers"])
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_booking_success_admin(test_admin_user, test_user, test_room, db_session):
    """Test that an admin can delete any booking."""
    from app.services.bookingService import BookingService

    booking_create = {
        "room_id": test_room["id"],
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=2),
        "nbr_people": 3,
        "breakfast": True
    }
    from app.schemas.bookingSchemas import BookingCreate
    booking_create_pydantic = BookingCreate(**booking_create)

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create_pydantic, userReponse)

    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.delete(f"/bookings/{booking.id}", headers=test_admin_user["headers"])

    assert response.status_code == 204, f"Expected 204, got {response.status_code}, response: {response.text}"

    async with AsyncClient(base_url=BASE_URL) as ac:
        get_response = await ac.get(f"/bookings/{booking.id}", headers=test_admin_user["headers"])
    assert get_response.status_code == 404

@pytest.mark.asyncio
async def test_delete_booking_unauthorized(test_user, test_room, db_session):
    """Test that a user cannot delete another user's booking."""

    booking_create = {
        "room_id": test_room["id"],
        "start_date": date.today(),
        "end_date": date.today() + timedelta(days=2),
        "nbr_people": 2,
        "breakfast": False
    }
    booking_create_pydantic = BookingCreate(**booking_create)

    userReponse = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    booking = await BookingService.create_booking(db_session, booking_create_pydantic, userReponse)

    user_data = {
        "email": "deleteme@example.com",
        "pseudo": "deletemeuser",
        "password": "deletemepassword"
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        other_user = response.json()

        auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if auth_response.status_code == 200:
            other_token = auth_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}
    try:
        async with AsyncClient(base_url=BASE_URL) as ac:
            response = await ac.delete(f"/bookings/{booking.id}", headers=other_headers)

        assert response.status_code == 403, f"Expected 403, got {response.status_code}, response: {response.text}"
        assert response.json()["detail"] == "Not authorized to delete this booking"
    finally:
        async with AsyncClient(base_url=BASE_URL) as ac:
            delete_response = await ac.delete(f"/users/{other_user['id']}", headers=other_headers)
            assert delete_response.status_code == 204

@pytest.mark.asyncio
async def test_delete_booking_not_found(test_user):
    """Test that deleting a non-existent booking returns 404."""
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.delete("/bookings/999999", headers=test_user["headers"])

    assert response.status_code == 404, f"Expected 404, got {response.status_code}, response: {response.text}"
    assert response.json()["detail"] == "Booking not found"

@pytest.mark.asyncio
async def test_get_bookings_by_user_as_admin(test_admin_user, test_user, test_room, db_session):
    """Test that an admin can retrieve bookings for any user."""
    
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
    
    user_response = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    
    booking1 = await BookingService.create_booking(db_session, booking_create_1, user_response)
    booking2 = await BookingService.create_booking(db_session, booking_create_2, user_response)
    
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get(f"/bookings/user/{test_user['id']}", headers=test_admin_user["headers"])
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) == 2, f"Expected 2 bookings, got {len(bookings)}"
    assert any(b["id"] == booking1.id for b in bookings), "Booking1 not found in response"
    assert any(b["id"] == booking2.id for b in bookings), "Booking2 not found in response"

@pytest.mark.asyncio
async def test_get_bookings_by_user_as_self(test_user, test_room, db_session):
    """Test that a user can retrieve only their own bookings."""
    
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
    
    user_response = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
    
    booking1 = await BookingService.create_booking(db_session, booking_create_1, user_response)
    booking2 = await BookingService.create_booking(db_session, booking_create_2, user_response)
    
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get(f"/bookings/user/{test_user['id']}", headers=test_user["headers"])
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) == 2, f"Expected 2 bookings, got {len(bookings)}"
    assert any(b["id"] == booking1.id for b in bookings), "Booking1 not found in response"
    assert any(b["id"] == booking2.id for b in bookings), "Booking2 not found in response"

@pytest.mark.asyncio
async def test_get_bookings_by_user_unauthorized(test_user, test_room, db_session, test_admin_user):
    """Test that a user cannot retrieve another user's bookings."""
    
    user_data = {
        "email": "other_user_test@example.com",
        "pseudo": "otherusertest",
        "password": "otherpassword"
    }

    async with AsyncClient(base_url="http://localhost:8000/users") as ac:
        response = await ac.post("/", json=user_data)
        assert response.status_code == 201, f"Expected 201, got {response.status_code}, response: {response.text}"
        other_user = response.json()

        auth_response = await ac.post("/login", data={"username": user_data["pseudo"], "password": user_data["password"]})
        if auth_response.status_code == 200:
            other_token = auth_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}
    
    try:
        booking_create = BookingCreate(
            room_id=test_room["id"],
            start_date=date.today(),
            end_date=date.today() + timedelta(days=2),
            nbr_people=2,
            breakfast=True
        )
        user_response = UserResponse(id=test_user["id"], email=test_user["email"], pseudo=test_user["pseudo"])
        booking = await BookingService.create_booking(db_session, booking_create, user_response)
        
        async with AsyncClient(base_url=BASE_URL) as ac:
            response = await ac.get(f"/bookings/user/{test_user['id']}", headers=other_headers)
        
        assert response.status_code == 403, f"Expected 403, got {response.status_code}"
        assert response.json()["detail"] == "Not authorized to view these bookings"
    
    finally:
        async with AsyncClient(base_url=BASE_URL) as ac:
            delete_response = await ac.delete(f"/users/{other_user['id']}", headers=other_headers)
            assert delete_response.status_code == 204, f"Expected 204, got {delete_response.status_code}"

@pytest.mark.asyncio
async def test_get_bookings_by_user_admin_nonexistent_user(test_admin_user, db_session):
    """Test that an admin retrieves an empty list for a non-existent user."""
    
    non_existent_user_id = 999999
    
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get(f"/bookings/user/{non_existent_user_id}", headers=test_admin_user["headers"])
    
    assert response.status_code == 200, f"Expected 200, got {response.status_code}"
    bookings = response.json()
    assert isinstance(bookings, list)
    assert len(bookings) == 0, f"Expected 0 bookings, got {len(bookings)}"

@pytest.mark.asyncio
async def test_get_bookings_by_user_as_self_nonexistent_user(test_user, db_session):
    """Test that a user cannot retrieve bookings for a non-existent user, even if it's themselves."""

    non_existent_user_id = 999999
    assert non_existent_user_id != test_user["id"], "Non-existent user_id should differ from test_user's ID"
    
    async with AsyncClient(base_url=BASE_URL) as ac:
        response = await ac.get(f"/bookings/user/{non_existent_user_id}", headers=test_user["headers"])
    
    assert response.status_code == 403, f"Expected 403, got {response.status_code}"
    assert response.json()["detail"] == "Not authorized to view these bookings"
