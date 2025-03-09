from pydantic import BaseModel
from datetime import datetime

class HotelPictureBase(BaseModel):
    hotel_id: int
    uuid: str

class HotelPictureCreate(HotelPictureBase):
    pass

class HotelPictureResponse(HotelPictureBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
