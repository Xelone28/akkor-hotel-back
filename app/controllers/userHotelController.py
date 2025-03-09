from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.userHotelSchemas import UserHotelCreate
from app.services.userHotelService import UserHotelService
from app.managers.databaseManager import get_db
from app.security import get_current_user

router = APIRouter(prefix="/user-hotels", tags=["UserHotels"])

@router.post("/", response_model=UserHotelCreate, status_code=201)
async def assign_owner(user_hotel_data: UserHotelCreate, db: AsyncSession = Depends(get_db)):
    """Assign a user as an owner of a hotel."""
    try:
        return await UserHotelService.assign_owner(db, user_hotel_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/", status_code=204)
async def remove_owner(user_id: int, hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Remove a user from hotel ownership."""
    deleted = await UserHotelService.remove_owner(db, user_id, hotel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Ownership relation not found")
