from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.hotelModel import Hotel
from app.schemas.hotelSchemas import HotelCreate, HotelUpdate, HotelResponse
from typing import List, Optional

class HotelService:

    @staticmethod
    async def get_hotel(db: AsyncSession, hotel_id: int) -> Optional[HotelResponse]:
        """Retrieve a hotel by ID."""
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        hotel = result.scalars().first()
        return HotelResponse.model_validate(hotel) if hotel else None

    @staticmethod
    async def get_hotels(
        db: AsyncSession, 
        name: Optional[str] = None, 
        address: Optional[str] = None, 
        limit: int = 10, 
        offset: int = 0
    ) -> List[HotelResponse]:
        """Retrieve hotels with optional filtering by name and address, and pagination."""
        
        query = select(Hotel)

        if name:
            query = query.filter(Hotel.name.ilike(f"%{name}%"))
        if address:
            query = query.filter(Hotel.address.ilike(f"%{address}%"))

        query = query.limit(limit).offset(offset)

        result = await db.execute(query)
        hotels = result.scalars().all()

        return [HotelResponse.model_validate(hotel) for hotel in hotels]


    @staticmethod
    async def create_hotel(db: AsyncSession, hotel_data: HotelCreate, user_id: int) -> HotelResponse:
        """Create a hotel and assign the user as owner."""
        new_hotel = Hotel(**hotel_data.model_dump())

        db.add(new_hotel)
        try:
            await db.commit()
            await db.refresh(new_hotel)

            return HotelResponse.model_validate(new_hotel)
        except IntegrityError:
            await db.rollback()
            raise ValueError("A hotel with this name or address might already exist.")
        
    @staticmethod
    async def update_hotel(db: AsyncSession, hotel_id: int, update_data: HotelUpdate) -> Optional[HotelResponse]:
        """Update hotel details."""
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        hotel = result.scalars().first()

        if not hotel:
            return None

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(hotel, key, value)

        try:
            await db.commit()
            await db.refresh(hotel)
            return HotelResponse.model_validate(hotel)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Unable to update hotel due to integrity constraints.")

    @staticmethod
    async def delete_hotel(db: AsyncSession, hotel_id: int) -> bool:
        """Delete a hotel."""
        result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
        hotel = result.scalars().first()

        if not hotel:
            return False
        
        await db.delete(hotel)
        await db.commit()
        return True
