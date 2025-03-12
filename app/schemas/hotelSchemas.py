from pydantic import BaseModel, condecimal, ConfigDict
from typing import Optional

class HotelBase(BaseModel):
    name: str
    address: str
    description: Optional[str] = None
    rating: Optional[condecimal(max_digits=2, decimal_places=1)] = None 
    breakfast: bool = False

class HotelCreate(HotelBase):
    pass

class HotelUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    description: Optional[str] = None
    rating: Optional[condecimal(max_digits=2, decimal_places=1)] = None
    breakfast: Optional[bool] = None

class HotelResponse(HotelBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

