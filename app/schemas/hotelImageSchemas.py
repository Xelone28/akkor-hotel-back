from pydantic import BaseModel, HttpUrl
from datetime import datetime

class HotelImageBase(BaseModel):
    filename: str

class HotelImageCreate(BaseModel):
    pass

class HotelImageResponse(BaseModel):
    id: int
    filename: str
    url: HttpUrl
    hotel_id: int
    uploaded_at: datetime

    class Config:
        from_attributes=True

class HotelImageListResponse(BaseModel):
    images: list[HotelImageResponse]