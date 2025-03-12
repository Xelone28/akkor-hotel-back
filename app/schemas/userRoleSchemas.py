from pydantic import BaseModel, ConfigDict

class UserRoleBase(BaseModel):
    user_id: int
    is_admin: bool

class UserRoleCreate(UserRoleBase):
    pass

class UserRoleResponse(UserRoleBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
