import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from databases import Database

# Initialize SQLAlchemy base (important for Alembic)
Base = declarative_base()

class DatabaseManager:
    _instance = None
    
    def __new__(cls, database_url: str = None):
        """Singleton pattern for managing database connections."""
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)

            db_url = database_url or os.getenv("DATABASE_URL")

            if not db_url:
                raise ValueError("DATABASE_URL is not set")

            cls._instance.engine = create_async_engine(db_url, echo=True)
            cls._instance.async_session = sessionmaker(
                cls._instance.engine,
                class_=AsyncSession,
                expire_on_commit=False
            )
            cls._instance.database = Database(db_url)

        return cls._instance

    async def connect(self):
        """Connect to the database asynchronously."""
        if not self.database.is_connected:
            await self.database.connect()

    async def disconnect(self):
        """Disconnect from the database asynchronously."""
        if self.database.is_connected:
            await self.database.disconnect()

async def get_db(database_url: str = None):
    """Dependency for getting a DB session with optional parameter."""
    db_manager = DatabaseManager(database_url)
    async with db_manager.async_session() as session:
        yield session