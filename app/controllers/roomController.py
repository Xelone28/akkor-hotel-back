from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.roomSchemas import RoomCreate, RoomUpdate, RoomResponse
from app.services.roomService import RoomService
from app.services.userRoleService import UserRoleService
from app.managers.databaseManager import get_db
from app.security import get_current_user
from typing import List

router = APIRouter(prefix="/rooms", tags=["Rooms"])

@router.get("/{room_id}", response_model=RoomResponse)
async def get_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a room by ID."""
    room = await RoomService.get_room(db, room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.get("/hotel/{hotel_id}", response_model=List[RoomResponse])
async def get_rooms_by_hotel(hotel_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve all rooms in a given hotel."""
    return await RoomService.get_rooms_by_hotel(db, hotel_id)

@router.post("/", response_model=RoomResponse, status_code=201)
async def create_room(
    room_data: RoomCreate, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a room - Admins only."""
    
    user_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not user_role or not user_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can create rooms.")

    try:
        return await RoomService.create_room(db, room_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(
    room_id: int, 
    update_data: RoomUpdate, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a room - Admins only."""
    
    user_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not user_role or not user_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can update rooms.")

    room = await RoomService.update_room(db, room_id, update_data)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.delete("/{room_id}", status_code=204)
async def delete_room(
    room_id: int, 
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a room - Admins only."""

    user_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not user_role or not user_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can delete rooms.")

    deleted = await RoomService.delete_room(db, room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")