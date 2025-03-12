from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.bookingSchemas import BookingCreate, BookingUpdate, BookingResponse
from app.schemas.userSchemas import UserResponse
from app.services.bookingService import BookingService
from app.services.userService import UserService
from app.managers.databaseManager import get_db
from app.security import get_current_user

router = APIRouter(prefix="/bookings", tags=["Bookings"])

@router.get("/", response_model=List[BookingResponse])
async def get_all_bookings(db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    """Retrieve bookings. Admins see all bookings; users see their own."""
    return await BookingService.get_bookings(db, current_user)

@router.get("/{booking_id}", response_model=BookingResponse)
async def get_booking(booking_id: int, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    """Retrieve a specific booking by ID."""
    booking = await BookingService.get_booking(db, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    
    # Authorization check
    if booking.user_id != current_user.id and not await UserService.is_admin(db, current_user.id):
        raise HTTPException(status_code=403, detail="Not authorized to view this booking")

    return booking

@router.post("/", response_model=BookingResponse, status_code=201)
async def create_booking(booking_data: BookingCreate, db: AsyncSession = Depends(get_db), current_user: UserResponse = Depends(get_current_user)):
    """Create a new booking. Authentication required."""
    return await BookingService.create_booking(db, booking_data, current_user)

@router.patch("/{booking_id}", response_model=BookingResponse)
async def update_booking(
    booking_id: int,
    booking_data: BookingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update an existing booking. Only the creator or admin can update."""
    return await BookingService.update_booking(db, booking_id, booking_data, current_user)

@router.delete("/{booking_id}", status_code=204)
async def delete_booking(
    booking_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a booking. Only the creator or admin can delete."""
    success = await BookingService.delete_booking(db, booking_id, current_user)
    if not success:
        raise HTTPException(status_code=500, detail="Error deleting booking")

@router.get("/user/{user_id}", response_model=List[BookingResponse])
async def get_bookings_by_user(
    user_id: int, 
    db: AsyncSession = Depends(get_db), 
    current_user: UserResponse = Depends(get_current_user)
):
    """Retrieve bookings for a specific user. Admins can retrieve any user's bookings; users can retrieve only their own."""
    
    is_admin = await UserService.is_admin(db, current_user.id)
    if not is_admin and current_user.id != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to view these bookings")
    
    bookings = await BookingService.get_bookings_by_user(db, user_id)
    return bookings
