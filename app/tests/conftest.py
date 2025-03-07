import pytest
from app.managers.databaseManager import DatabaseManager
from app.managers.s3Manager import S3Manager
from fastapi.testclient import TestClient
from app.main import app
import pytest_asyncio


@pytest_asyncio.fixture()
async def setup_database():
    db_manager = DatabaseManager()
    await db_manager.connect()
    yield
    await db_manager.disconnect()

@pytest.fixture()
def client():
    return TestClient(app)

@pytest.fixture()
def s3_mock(mocker):
    mock_s3 = mocker.patch.object(S3Manager, '_instance', None)  # Reset singleton
    return S3Manager()
