# src/test/test_user_model.py
import pytest
from sqlalchemy import text
from src.main.models import User

@pytest.mark.asyncio
async def test_db_connection(async_session):
    result = await async_session.execute(text("SELECT 1"))
    value = result.scalar_one()
    assert value == 1

@pytest.mark.asyncio
async def test_create_user(async_session):
    test_user = User(
        username="testuser",
        email="test@example.com",
        first_name="Test",
        last_name="User",
        password="testpassword"
    )
    
    async_session.add(test_user)
    await async_session.commit()

    result = await async_session.execute(
        text("SELECT username FROM users WHERE email = :email"),
        {"email": "test@example.com"}
    )
    username = result.scalar_one()
    assert username == "testuser"
    
    
@pytest.mark.asyncio
async def test_update_user(async_session):
    # Test updating user information
    test_user = User(
        username="updatetest",
        email="update@example.com",
        first_name="Before",
        last_name="Update",
        password="testpass"
    )
    async_session.add(test_user)
    await async_session.commit()
    
    test_user.first_name = "After"
    await async_session.commit()
    
    result = await async_session.execute(
        text("SELECT first_name FROM users WHERE email = :email"),
        {"email": "update@example.com"}
    )
    updated_name = result.scalar_one()
    assert updated_name == "After"

@pytest.mark.asyncio
async def test_disable_user(async_session):
    # Test disabling a user
    test_user = User(
        username="disabletest",
        email="disable@example.com",
        first_name="Disable",
        last_name="Test",
        password="testpass"
    )
    async_session.add(test_user)
    await async_session.commit()
    
    test_user.enabled = False
    await async_session.commit()
    
    result = await async_session.execute(
        text("SELECT enabled FROM users WHERE email = :email"),
        {"email": "disable@example.com"}
    )
    is_enabled = result.scalar_one()
    assert not is_enabled

@pytest.mark.asyncio
async def test_unique_constraints(async_session):
    # Test that unique constraints are working
    user1 = User(
        username="uniquetest",
        email="unique@example.com",
        first_name="Unique",
        last_name="Test",
        password="testpass"
    )
    async_session.add(user1)
    await async_session.commit()
    
    with pytest.raises(Exception):  # Should raise on duplicate username/email
        user2 = User(
            username="uniquetest",  # Same username
            email="different@example.com",
            first_name="Another",
            last_name="User",
            password="testpass"
        )
        async_session.add(user2)
        await async_session.commit()