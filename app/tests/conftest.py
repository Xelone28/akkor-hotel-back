import os
import pytest
from dotenv import load_dotenv
from app.managers.databaseManager import DatabaseManager
from app.managers.s3Manager import S3Manager
from fastapi.testclient import TestClient
from app.main import app
import pytest_asyncio

load_dotenv()

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")

@pytest_asyncio.fixture()
async def setup_database():
    db_manager = DatabaseManager(TEST_DATABASE_URL)
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
