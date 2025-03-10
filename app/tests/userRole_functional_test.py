import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.userRoleSchemas import UserRoleCreate
from app.services.userRoleService import UserRoleService


@pytest.mark.asyncio
async def test_assign_role(db_session: AsyncSession, test_user):
    """Test assigning a role to a user."""
    role_data = UserRoleCreate(user_id=test_user["id"], is_admin=True)
    role = await UserRoleService.assign_role(db_session, role_data)

    assert role.id is not None
    assert role.user_id == test_user["id"]
    assert role.is_admin is True

@pytest.mark.asyncio
async def test_get_user_role(db_session: AsyncSession, test_user):
    """Test retrieving a user role."""
    role_data = UserRoleCreate(user_id=test_user["id"], is_admin=False)
    await UserRoleService.assign_role(db_session, role_data)

    role = await UserRoleService.get_role_by_user(db_session, test_user["id"])
    assert role is not None
    assert role.user_id == test_user["id"]
    assert role.is_admin is False

@pytest.mark.asyncio
async def test_delete_role(db_session: AsyncSession, test_user):
    """Test removing a role from a user."""
    role_data = UserRoleCreate(user_id=test_user["id"], is_admin=True)
    await UserRoleService.assign_role(db_session, role_data)

    deleted = await UserRoleService.delete_role(db_session, test_user["id"])
    assert deleted is True

    role = await UserRoleService.get_role_by_user(db_session, test_user["id"])
    assert role is None
