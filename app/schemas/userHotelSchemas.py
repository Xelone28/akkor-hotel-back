from pydantic import BaseModel

class UserHotelCreate(BaseModel):
    user_id: int
    hotel_id: int

class UserHotelResponse(UserHotelCreate):
    pass
