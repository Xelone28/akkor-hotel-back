from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.hotelPictureModel import HotelPicture
from app.schemas.hotelPictureSchemas import HotelPictureCreate, HotelPictureResponse
from app.managers.s3Manager import S3Manager
from typing import List

class HotelPictureService:

    @staticmethod
    async def add_picture(db: AsyncSession, picture_data: HotelPictureCreate) -> HotelPictureResponse:
        """Add a picture UUID to a hotel."""
        new_picture = HotelPicture(**picture_data.model_dump())
        db.add(new_picture)
        await db.commit()
        await db.refresh(new_picture)
        return HotelPictureResponse(
            id=new_picture.id,
            hotel_id=new_picture.hotel_id,
            image_url=S3Manager().get_file_url(new_picture.uuid),  # ✅ Uses the Public CDN URL
            created_at=new_picture.created_at
        )

    @staticmethod
    async def get_pictures_by_hotel(db: AsyncSession, hotel_id: int) -> List[HotelPictureResponse]:
        """Retrieve all pictures for a specific hotel."""
        result = await db.execute(select(HotelPicture).filter(HotelPicture.hotel_id == hotel_id))
        pictures = result.scalars().all()

        s3_manager = S3Manager()
        return [
            HotelPictureResponse(
                id=p.id,
                hotel_id=p.hotel_id,
                image_url=s3_manager.get_file_url(p.uuid),  # ✅ Uses Public CDN URL
                created_at=p.created_at
            )
            for p in pictures
        ]