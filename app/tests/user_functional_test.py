import pytest
from app.schemas.userSchemas import UserCreate, UserUpdate
from app.services.userService import UserService

@pytest.mark.asyncio
async def test_create_user(db_session):
    """Tests user creation"""
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
    """Test to get a user by id."""
    found_user = await UserService.get_user(db_session, test_user["id"])
    
    assert found_user is not None
    assert found_user.id == test_user["id"]
    assert found_user.email == test_user["email"]

@pytest.mark.asyncio
async def test_get_users(db_session, test_user):
    """Test to recover every user."""
    users = await UserService.get_users(db_session)

    assert len(users) > 0
    assert any(user.id == test_user["id"] for user in users)

@pytest.mark.asyncio
async def test_update_user(db_session, test_user):
    """Test that user data can be updated."""
    update_data = UserUpdate(email="updated@example.com", pseudo="updateduser")

    updated_user = await UserService.update_user(db_session, test_user["id"], update_data)

    assert updated_user is not None
    assert updated_user.email == "updated@example.com"
    assert updated_user.pseudo == "updateduser"

@pytest.mark.asyncio
async def test_get_user_by_email(db_session, test_user):
    """Tests that we can recover a user by email."""
    found_user = await UserService.get_user_by_email(db_session, test_user["email"])

    assert found_user is not None
    assert found_user.id == test_user["id"]

@pytest.mark.asyncio
async def test_get_user_by_pseudo(db_session, test_user):
    """Tests that we can recover a user by pseudo."""
    found_user = await UserService.get_user_by_pseudo(db_session, test_user["pseudo"])

    assert found_user is not None
    assert found_user.id == test_user["id"]
