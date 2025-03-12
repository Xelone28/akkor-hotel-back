from pydantic import BaseModel, ConfigDict
from datetime import date
from typing import Optional

class BookingBase(BaseModel):
    room_id: int
    start_date: date
    end_date: date
    nbr_people: int
    breakfast: Optional[bool] = False

class BookingCreate(BookingBase):
    pass

class BookingUpdate(BaseModel):
    room_id: Optional[int] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    nbr_people: Optional[int] = None
    breakfast: Optional[bool] = None

class BookingResponse(BaseModel):
    id: int
    user_id: int
    room_id: int
    start_date: date
    end_date: date
    nbr_people: int
    breakfast: bool

    model_config = ConfigDict(from_attributes=True)

