import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.schemas.userSchemas import UserCreate
from app.managers.databaseManager import Base
from httpx import AsyncClient
from app.main import app
import os
from dotenv import load_dotenv
from app.services.userService import UserService

load_dotenv()

TEST_DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_async_engine(TEST_DATABASE_URL, echo=True, future=True)
TestingSessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(scope="module")
async def init_db():
    """Initialise la base de données pour les tests fonctionnels"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)  # ✅ Création des tables

    yield

@pytest.fixture(scope="function")
async def db_session():
    """Crée une session isolée pour chaque test fonctionnel."""
    async with TestingSessionLocal() as session:
        yield session
        await session.rollback()  # ✅ Empêche la persistance en base après les tests ???


@pytest.fixture(scope="function")
async def client():
    """Crée un client HTTP async pour tester l'API."""
    async with AsyncClient(app=app, base_url="http://localhost:8000") as ac:
        yield ac

# @pytest.mark.asyncio
# async def test_create_user(db_session):
#     """Teste la création d'un utilisateur."""
#     user_data = UserCreate(
#         email="newuser@example.com",
#         pseudo="newuser",
#         password="securepassword"
#     )

#     user = await UserService.create_user(db_session, user_data)

#     assert user.id is not None
#     assert user.email == "newuser@example.com"
#     assert user.pseudo == "newuser"