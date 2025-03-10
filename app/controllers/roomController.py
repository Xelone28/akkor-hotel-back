from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.roomSchemas import RoomCreate, RoomUpdate, RoomResponse
from app.services.roomService import RoomService
from app.managers.databaseManager import get_db
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
async def create_room(room_data: RoomCreate, db: AsyncSession = Depends(get_db)):
    """Create a room."""
    try:
        return await RoomService.create_room(db, room_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.patch("/{room_id}", response_model=RoomResponse)
async def update_room(room_id: int, update_data: RoomUpdate, db: AsyncSession = Depends(get_db)):
    """Update a room."""
    room = await RoomService.update_room(db, room_id, update_data)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    return room

@router.delete("/{room_id}", status_code=204)
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    """Delete a room."""
    deleted = await RoomService.delete_room(db, room_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Room not found")
