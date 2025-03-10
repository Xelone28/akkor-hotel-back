import pytest
from app.managers.databaseManager import DatabaseManager

@pytest.mark.asyncio
async def test_database_connection():
    db_manager = DatabaseManager()

    await db_manager.connect()
    assert db_manager.database.is_connected

    await db_manager.disconnect()
    assert not db_manager.database.is_connected
