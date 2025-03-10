from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.userRoleModel import UserRole
from app.schemas.userRoleSchemas import UserRoleCreate, UserRoleResponse
from typing import Optional

class UserRoleService:

    @staticmethod
    async def assign_role(db: AsyncSession, role_data: UserRoleCreate) -> UserRoleResponse:
        """Assign a role to a user."""
        new_role = UserRole(**role_data.model_dump())
        db.add(new_role)
        await db.commit()
        await db.refresh(new_role)
        return UserRoleResponse.model_validate(new_role)

    @staticmethod
    async def get_role_by_user(db: AsyncSession, user_id: int) -> Optional[UserRoleResponse]:
        """Retrieve a user's role by user ID."""
        result = await db.execute(select(UserRole).filter(UserRole.user_id == user_id))
        role = result.scalars().first()
        return UserRoleResponse.model_validate(role) if role else None

    @staticmethod
    async def delete_role(db: AsyncSession, user_id: int) -> bool:
        """Remove a role from a user."""
        result = await db.execute(select(UserRole).filter(UserRole.user_id == user_id))
        role = result.scalars().first()

        if not role:
            return False

        await db.delete(role)
        await db.commit()
        return True
