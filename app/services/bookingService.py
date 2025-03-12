from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.bookingModel import Booking
from app.schemas.bookingSchemas import BookingCreate, BookingUpdate, BookingResponse
from app.schemas.userSchemas import UserResponse
from app.services.userService import UserService
from app.services.roomService import RoomService
from fastapi import HTTPException, status

class BookingService:

    @staticmethod
    async def get_booking(db: AsyncSession, booking_id: int) -> Optional[BookingResponse]:
        """Retrieve a booking by its ID."""
        result = await db.execute(select(Booking).filter(Booking.id == booking_id))
        booking = result.scalars().first()
        return BookingResponse.from_orm(booking) if booking else None

    @staticmethod
    async def get_bookings(db: AsyncSession, current_user: UserResponse) -> List[BookingResponse]:
        """Retrieve all bookings. Admins get all bookings, users get their own."""
        if await UserService.is_admin(db, current_user.id):
            result = await db.execute(select(Booking))
        else:
            result = await db.execute(select(Booking).filter(Booking.user_id == current_user.id))
        bookings = result.scalars().all()
        return [BookingResponse.from_orm(booking) for booking in bookings]

    @staticmethod
    async def create_booking(db: AsyncSession, booking_data: BookingCreate, current_user: UserResponse) -> BookingResponse:
        """Create a new booking linked to the current user."""
        
        room = await RoomService.get_room(db, booking_data.room_id)
        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        new_booking = Booking(
            user_id=current_user.id,
            room_id=booking_data.room_id,
            start_date=booking_data.start_date,
            end_date=booking_data.end_date,
            nbr_people=booking_data.nbr_people,
            breakfast=booking_data.breakfast
        )

        db.add(new_booking)
        try:
            await db.commit()
            await db.refresh(new_booking)
            return BookingResponse.from_orm(new_booking)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Invalid booking data.")

    @staticmethod
    async def update_booking(db: AsyncSession, booking_id: int, booking_data: BookingUpdate, current_user: UserResponse) -> Optional[BookingResponse]:
        """Update an existing booking if authorized."""
        booking = await db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.user_id != current_user.id and not await UserService.is_admin(db, current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to update this booking")

        for key, value in booking_data.dict(exclude_unset=True).items():
            setattr(booking, key, value)
        
        try:
            await db.commit()
            await db.refresh(booking)
            return BookingResponse.from_orm(booking)
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Invalid booking data.")

    @staticmethod
    async def delete_booking(db: AsyncSession, booking_id: int, current_user: UserResponse) -> bool:
        """Delete a booking if authorized."""
        booking = await db.get(Booking, booking_id)
        if not booking:
            raise HTTPException(status_code=404, detail="Booking not found")
        
        if booking.user_id != current_user.id and not await UserService.is_admin(db, current_user.id):
            raise HTTPException(status_code=403, detail="Not authorized to delete this booking")

        await db.delete(booking)
        await db.commit()
        return True
    
    @staticmethod
    async def get_bookings_by_user(db: AsyncSession, user_id: int) -> List[BookingResponse]:
        """Retrieve all bookings for a specific user."""
        result = await db.execute(select(Booking).filter(Booking.user_id == user_id))
        bookings = result.scalars().all()
        return [BookingResponse.from_orm(booking) for booking in bookings]

