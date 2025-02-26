import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from databases import Database

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is not set")

class DatabaseManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseManager, cls).__new__(cls)
            cls._instance.engine = create_async_engine(DATABASE_URL, echo=True)
            cls._instance.async_session = sessionmaker(
                cls._instance.engine,
                expire_on_commit=False
            )
            cls._instance.database = Database(DATABASE_URL)
        return cls._instance

    async def connect(self):
        if not self.database.is_connected:
            await self.database.connect()

    async def disconnect(self):
        if self.database.is_connected:
            await self.database.disconnect()