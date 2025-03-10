from pydantic import BaseModel

class UserRoleBase(BaseModel):
    user_id: int
    is_admin: bool

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleResponse(UserRoleBase):
    id: int

    class Config:
        from_attributes = True
