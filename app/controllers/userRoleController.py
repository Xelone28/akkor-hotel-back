from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.userRoleSchemas import UserRoleCreate, UserRoleResponse
from app.services.userRoleService import UserRoleService
from app.managers.databaseManager import get_db
from app.security import get_current_user
from typing import Optional

router = APIRouter(prefix="/user-roles", tags=["User Roles"])

@router.post("/", response_model=UserRoleResponse, status_code=201)
async def assign_role(
    role_data: UserRoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Assign a role to a user - Admins only."""
    
    admin_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not admin_role or not admin_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can assign roles.")

    return await UserRoleService.assign_role(db, role_data)

@router.get("/{user_id}", response_model=Optional[UserRoleResponse])
async def get_user_role(user_id: int, db: AsyncSession = Depends(get_db)):
    """Retrieve a user's role."""
    return await UserRoleService.get_role_by_user(db, user_id)

@router.delete("/{user_id}", status_code=204)
async def delete_user_role(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Remove an assigned role from a user - Admins only."""

    admin_role = await UserRoleService.get_role_by_user(db, current_user.id)
    if not admin_role or not admin_role.is_admin:
        raise HTTPException(status_code=403, detail="Only admins can remove roles.")

    deleted = await UserRoleService.delete_role(db, user_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="User role not found")