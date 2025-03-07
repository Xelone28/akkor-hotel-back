import time
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.userSchemas import UserCreate, UserUpdate
from app.managers.databaseManager import Base
from httpx import AsyncClient
from app.main import app
import os
from dotenv import load_dotenv
from app.services.userService import UserService
from sqlalchemy.pool import NullPool

load_dotenv()

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

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
        email="testuser@example.com",
        pseudo="testuser",
        password="securepassword"
    )
    user = await UserService.create_user(db_session, user_data)
    yield user  # Fournit l'utilisateur pour les tests
    success = await UserService.delete_user(db_session, user.id)
    assert success is True



@pytest.mark.asyncio
async def test_create_user(db_session):
    """Teste la création d'un utilisateur."""
    user_data = UserCreate(
        email="newuser@example.com",
        pseudo="newuser",
        password="securepassword"
    )

    user = await UserService.create_user(db_session, user_data)

    assert user.id is not None
    assert user.email == "newuser@example.com"
    assert user.pseudo == "newuser"

@pytest.mark.asyncio
async def test_get_user(db_session, test_user):
    """Vérifie qu'on peut récupérer un utilisateur par ID."""
    found_user = await UserService.get_user(db_session, test_user.id)
    
    assert found_user is not None
    assert found_user.id == test_user.id
    assert found_user.email == test_user.email

@pytest.mark.asyncio
async def test_get_users(db_session, test_user):
    """Vérifie qu'on peut récupérer tous les utilisateurs."""
    users = await UserService.get_users(db_session)

    assert len(users) > 0
    assert any(user.id == test_user.id for user in users)

@pytest.mark.asyncio
async def test_update_user(db_session, test_user):
    """Vérifie que les informations d'un utilisateur peuvent être mises à jour."""
    update_data = UserUpdate(email="updated@example.com", pseudo="updateduser")

    updated_user = await UserService.update_user(db_session, test_user.id, update_data)

    assert updated_user is not None
    assert updated_user.email == "updated@example.com"
    assert updated_user.pseudo == "updateduser"

@pytest.mark.asyncio
async def test_get_user_by_email(db_session, test_user):
    """Vérifie qu'on peut récupérer un utilisateur par email."""
    found_user = await UserService.get_user_by_email(db_session, test_user.email)

    assert found_user is not None
    assert found_user.id == test_user.id

@pytest.mark.asyncio
async def test_get_user_by_pseudo(db_session, test_user):
    """Vérifie qu'on peut récupérer un utilisateur par pseudo."""
    found_user = await UserService.get_user_by_pseudo(db_session, test_user.pseudo)

    assert found_user is not None
    assert found_user.id == test_user.id
