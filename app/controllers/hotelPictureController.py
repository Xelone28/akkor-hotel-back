from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.hotelPictureSchemas import HotelPictureCreate, HotelPictureResponse
from app.services.hotelPictureService import HotelPictureService
from app.managers.databaseManager import get_db
from typing import List

router = APIRouter(prefix="/hotel-pictures", tags=["Hotel Pictures"])

@router.post("/", response_model=HotelPictureResponse, status_code=201)
async def add_picture_to_hotel(picture_data: HotelPictureCreate, db: AsyncSession = Depends(get_db)):
    """Attach a picture to a hotel."""
    return await HotelPictureService.add_picture(db, picture_data)

@router.get("/{hotel_id}", response_model=List[HotelPictureResponse])
async def get_hotel_pictures(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve all pictures associated with a hotel."""
    return await HotelPictureService.get_pictures_by_hotel(db, hotel_id)

@router.delete("/{picture_id}", status_code=204)
async def delete_hotel_picture(picture_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a specific picture from a hotel."""
    deleted = await HotelPictureService.delete_picture(db, picture_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Picture not found")
