from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.roomModel import Room
from app.schemas.roomSchemas import RoomCreate, RoomUpdate, RoomResponse
from typing import List, Optional

class RoomService:

    @staticmethod
    async def get_room(db: AsyncSession, room_id: int) -> Optional[RoomResponse]:
        """Retrieve a room by ID."""
        result = await db.execute(select(Room).filter(Room.id == room_id))
        room = result.scalars().first()
        return RoomResponse.model_validate(room) if room else None

    @staticmethod
    async def get_rooms_by_hotel(db: AsyncSession, hotel_id: int) -> List[RoomResponse]:
        """Retrieve all rooms for a specific hotel."""
        result = await db.execute(select(Room).filter(Room.hotel_id == hotel_id))
        rooms = result.scalars().all()
        return [RoomResponse.model_validate(room) for room in rooms]

    @staticmethod
    async def create_room(db: AsyncSession, room_data: RoomCreate) -> RoomResponse:
        """Create a new room."""
        new_room = Room(**room_data.model_dump())
        
        db.add(new_room)
        try:
            await db.commit()
            await db.refresh(new_room)
            return RoomResponse.model_validate(new_room)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Integrity error while adding the room.")

    @staticmethod
    async def update_room(db: AsyncSession, room_id: int, update_data: RoomUpdate) -> Optional[RoomResponse]:
        """Update a room."""
        result = await db.execute(select(Room).filter(Room.id == room_id))
        room = result.scalars().first()

        if not room:
            return None

        for key, value in update_data.model_dump(exclude_unset=True).items():
            setattr(room, key, value)

        try:
            await db.commit()
            await db.refresh(room)
            return RoomResponse.model_validate(room)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Integrity error updating room.")

    @staticmethod
    async def delete_room(db: AsyncSession, room_id: int) -> bool:
        """Delete a room."""
        result = await db.execute(select(Room).filter(Room.id == room_id))
        room = result.scalars().first()
        
        if not room:
            return False

        await db.delete(room)
        await db.commit()
        return True
