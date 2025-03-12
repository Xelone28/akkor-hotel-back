from pydantic import BaseModel, condecimal, ConfigDict
from typing import Optional

class RoomBase(BaseModel):
    hotel_id: int
    price: condecimal(max_digits=10, decimal_places=2)
    number_of_beds: int

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    price: Optional[condecimal(max_digits=10, decimal_places=2)] = None
    number_of_beds: Optional[int] = None

class RoomResponse(RoomBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

