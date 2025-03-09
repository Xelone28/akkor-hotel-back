from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.userHotelModel import UserHotel
from app.schemas.userHotelSchemas import UserHotelCreate
from typing import Optional

class UserHotelService:

    @staticmethod
    async def assign_owner(db: AsyncSession, user_hotel_data: UserHotelCreate) -> UserHotelCreate:
        """Assign a user as owner of a hotel."""
        new_relation = UserHotel(**user_hotel_data.model_dump())

        db.add(new_relation)
        try:
            await db.commit()
            return user_hotel_data
        except IntegrityError:
            await db.rollback()
            raise ValueError("This ownership assignment already exists.")

    @staticmethod
    async def remove_owner(db: AsyncSession, user_id: int, hotel_id: int) -> bool:
        """Remove a user from hotel ownership."""
        result = await db.execute(select(UserHotel).filter(UserHotel.user_id == user_id, UserHotel.hotel_id == hotel_id))
        relation = result.scalars().first()

        if not relation:
            return False

        await db.delete(relation)
        await db.commit()
        return True

    @staticmethod
    async def is_owner(db: AsyncSession, user_id: int, hotel_id: int) -> bool:
        """Check if a user is the owner of a hotel."""
        result = await db.execute(select(UserHotel).filter(UserHotel.user_id == user_id, UserHotel.hotel_id == hotel_id))
        return result.scalars().first() is not None
