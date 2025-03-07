import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

# Initialize SQLAlchemy base (important for Alembic)
Base = declarative_base()

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.engine = create_async_engine(DATABASE_URL, echo=True)
            cls._instance.async_session = sessionmaker(
                cls._instance.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            cls._instance.database = Database(DATABASE_URL)  # FastAPI's databases library

        return cls._instance

    async def connect(self):
        """Connect to the database asynchronously."""
        if not self.database.is_connected:
            await self.database.connect()

    async def disconnect(self):
        """Disconnect from the database asynchronously."""
        if self.database.is_connected:
            await self.database.disconnect()

# Dependency for FastAPI
async def get_db():
    """Dependency for getting a DB session."""
    async with DatabaseManager().async_session() as session:
        yield session