from pydantic import BaseModel, EmailStr
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    pseudo: str

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    pseudo: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None

class UserResponse(UserBase):
    id: int
    is_admin: Optional[bool] = False

    class Config:
        from_attributes = True
class UserWithRoleResponse(UserResponse):
    is_admin: bool