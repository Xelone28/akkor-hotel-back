import os
from dotenv import load_dotenv
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.userSchemas import UserCreate
from app.schemas.userRoleSchemas import UserRoleCreate
from app.services.userService import UserService
from app.services.userRoleService import UserRoleService
from sqlalchemy.pool import NullPool

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True, poolclass=NullPool)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

@pytest.fixture()
async def db_session():
    """Crée une session isolée pour chaque test fonctionnel."""
    async with TestingSessionLocal() as session:
        session.begin()
        yield session
        await session.commit()
        await session.close()

@pytest_asyncio.fixture(scope="function")
async def test_user(db_session):
    """Crée un utilisateur test."""
    user_data = UserCreate(
        email="04@example.com",
        pseudo="04",
        password="securepassword"
    )
    user = await UserService.create_user(db_session, user_data)
    yield user
    success = await UserService.delete_user(db_session, user.id)
    assert success is True

@pytest.mark.asyncio
async def test_assign_role(db_session: AsyncSession, test_user):
    """Test assigning a role to a user."""
    role_data = UserRoleCreate(user_id=test_user.id, is_admin=True)
    role = await UserRoleService.assign_role(db_session, role_data)

    assert role.id is not None
    assert role.user_id == test_user.id
    assert role.is_admin is True

@pytest.mark.asyncio
async def test_get_user_role(db_session: AsyncSession, test_user):
    """Test retrieving a user role."""
    role_data = UserRoleCreate(user_id=test_user.id, is_admin=False)
    await UserRoleService.assign_role(db_session, role_data)

    role = await UserRoleService.get_role_by_user(db_session, test_user.id)
    assert role is not None
    assert role.user_id == test_user.id
    assert role.is_admin is False

@pytest.mark.asyncio
async def test_delete_role(db_session: AsyncSession, test_user):
    """Test removing a role from a user."""
    role_data = UserRoleCreate(user_id=test_user.id, is_admin=True)
    await UserRoleService.assign_role(db_session, role_data)

    deleted = await UserRoleService.delete_role(db_session, test_user.id)
    assert deleted is True

    role = await UserRoleService.get_role_by_user(db_session, test_user.id)
    assert role is None
