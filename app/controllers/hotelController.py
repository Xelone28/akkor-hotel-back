from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.userSchemas import UserResponse
from app.schemas.hotelSchemas import HotelCreate, HotelUpdate, HotelResponse
from app.services.hotelService import HotelService
from app.services.userRoleService import UserRoleService
from app.managers.databaseManager import get_db
from typing import List
from app.security import get_current_user
from typing import Optional

router = APIRouter(prefix="/hotels", tags=["Hotels"])

@router.get("/search", response_model=List[HotelResponse])
async def search_hotels(
    name: Optional[str] = None,
    address: Optional[str] = None,
    limit: int = 10,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    """Search hotels by optional name and address filters with pagination."""
    return await HotelService.get_hotels(db, name=name, address=address, limit=limit, offset=offset)

@router.get("/{hotel_id}", response_model=HotelResponse)
async def get_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a hotel by ID."""
    hotel = await HotelService.get_hotel(db, hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.get("/", response_model=List[HotelResponse])
async def get_hotels(db: AsyncSession = Depends(get_db)):
    """Retrieve all hotels."""
    return await HotelService.get_hotels(db)

@router.post("/", response_model=HotelResponse, status_code=201)
async def create_hotel(
    hotel_data: HotelCreate, 
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Create a hotel - Only admins can do this."""
    
    user_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not user_role or not user_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create hotels.")

    try:
        return await HotelService.create_hotel(db, hotel_data, current_user.id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/{hotel_id}", response_model=HotelResponse)
async def update_hotel(
    hotel_id: int,
    update_data: HotelUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Update a hotel - Only admins can do this."""
    
    user_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not user_role or not user_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update hotel information.")

    hotel = await HotelService.update_hotel(db, hotel_id, update_data)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    return hotel

@router.delete("/{hotel_id}", status_code=204)
async def delete_hotel(
    hotel_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: UserResponse = Depends(get_current_user)
):
    """Delete a hotel - Only admins can do this."""

    user_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not user_role or not user_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete hotels.")

    deleted = await HotelService.delete_hotel(db, hotel_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Hotel not found")