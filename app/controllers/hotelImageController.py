from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, status, Response, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.services.hotelImageService import HotelImageService
from app.schemas.hotelImageSchemas import HotelImageResponse
from app.schemas.userSchemas import UserResponse
from app.managers.databaseManager import get_db
from app.security import get_current_user
from app.models.hotelModel import Hotel
from sqlalchemy.future import select

router = APIRouter(prefix="/hotels", tags=["Hotel Images"])

@router.post("/{hotel_id}/images/upload", response_model=HotelImageResponse, status_code=201)
async def upload_hotel_image(
    hotel_id: int,
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Upload an image to a specific hotel and save its metadata to the database.
    """

    result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")
    try:
        image = await HotelImageService.upload_image(db, file, hotel_id)
        return image
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

@router.get("/{hotel_id}/images/{image_id}", response_model=HotelImageResponse)
async def get_hotel_image(
    hotel_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db)
):
    """
    Retrieve a hotel image's metadata by its ID.
    """

    image = await HotelImageService.get_image(db, image_id)
    if not image or image.hotel_id != hotel_id:
        raise HTTPException(status_code=404, detail="Image not found for this hotel")
    return image

@router.delete("/{hotel_id}/images/{image_id}", status_code=204)
async def delete_hotel_image(
    hotel_id: int,
    image_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    Delete a hotel image. Only the owner or an admin can delete the image.
    """

    image = await HotelImageService.get_image(db, image_id)
    if not image or image.hotel_id != hotel_id:
        raise HTTPException(status_code=404, detail="Image not found for this hotel")

    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this image")

    success = await HotelImageService.delete_image(db, image_id)
    if not success:
        raise HTTPException(status_code=500, detail="Error deleting image")

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.get("/{hotel_id}/images", response_model=List[HotelImageResponse])
async def list_hotel_images(
    hotel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user),
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    """
    List all images for a specific hotel with pagination.
    """

    result = await db.execute(select(Hotel).filter(Hotel.id == hotel_id))
    hotel = result.scalars().first()
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    images = await HotelImageService.list_images(db, hotel_id=hotel_id)

    paginated_images = images[offset:offset + limit]
    return paginated_images
