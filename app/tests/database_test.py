import os
import pytest
from app.managers.databaseManager import DatabaseManager
from dotenv import load_dotenv

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

@pytest.mark.asyncio
async def test_database_connection():
    db_manager = DatabaseManager(TEST_DATABASE_URL)

    await db_manager.connect()
    assert db_manager.database.is_connected

    await db_manager.disconnect()
    assert not db_manager.database.is_connected
