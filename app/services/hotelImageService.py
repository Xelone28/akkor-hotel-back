import uuid
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import UploadFile, HTTPException
from app.models.hotelImageModel import HotelImage
from app.schemas.hotelImageSchemas import HotelImageResponse
from app.managers.s3Manager import S3Manager

class HotelImageService:

    @staticmethod
    async def upload_image(db: AsyncSession, file: UploadFile, hotel_id: int, public: bool = True) -> HotelImageResponse:
        """
        Uploads an image to S3 and saves its metadata to the database linked to a hotel.
        """
        s3_manager = S3Manager()

        unique_filename = f"{uuid.uuid4()}_{file.filename}"

        try:
            url = s3_manager.upload_file(file, object_name=unique_filename, public=public)

            new_image = HotelImage(
                filename=unique_filename,
                url=url,
                hotel_id=hotel_id
            )
            db.add(new_image)
            await db.commit()
            await db.refresh(new_image)
            return HotelImageResponse.from_orm(new_image)
        except IntegrityError:
            await db.rollback()
            raise ValueError("Image could not be uploaded due to a database error.")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to upload image: {str(e)}")
    
    @staticmethod
    async def delete_image(db: AsyncSession, image_id: int):
        """
        Deletes a hotel image from S3 and the database.
        """
        image = await db.get(HotelImage, image_id)
        if not image:
            raise ValueError("Image not found.")

        s3_manager = S3Manager()
        try:
            s3_manager.delete_file(image.filename)

            await db.delete(image)
            await db.commit()
            return True
        except HTTPException:
            raise
        except Exception as e:
            await db.rollback()
            raise HTTPException(status_code=500, detail=f"Failed to delete image: {str(e)}")

    @staticmethod
    async def get_image(db: AsyncSession, image_id: int) -> Optional[HotelImageResponse]:
        """
        Retrieves a hotel image by its ID.
        """
        result = await db.execute(select(HotelImage).filter(HotelImage.id == image_id))
        image = result.scalars().first()
        if image:
            return HotelImageResponse.from_orm(image)
        return None

    @staticmethod
    async def list_images(db: AsyncSession, hotel_id: Optional[int] = None) -> List[HotelImageResponse]:
        """
        Lists all images for a specific hotel, optionally filtering by hotel ID.
        """
        query = select(HotelImage)
        if hotel_id:
            query = query.filter(HotelImage.hotel_id == hotel_id)
        result = await db.execute(query)
        images = result.scalars().all()
        return [HotelImageResponse.from_orm(image) for image in images]