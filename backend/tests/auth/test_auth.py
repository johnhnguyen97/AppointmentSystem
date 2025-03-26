import pytest
import asyncio
import logging
import json
from typing import Dict, Any
import traceback
from src.main.auth import verify_password
from src.main.mutations import AuthMutations
from src.main.database import async_session
from sqlalchemy import select
from src.main.models import User

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MockInfo:
    """Mock Info object for GraphQL context."""
    def __init__(self):
        self.context = None

@pytest.mark.auth
async def test_password_verification():
    """Test the password verification function."""
    try:
        # Test with a known password hash (this is just a test, replace with actual hash format if different)
        test_password = "password123"

        # Get admin's stored password hash from database
        async with async_session() as session:
            query = select(User.password).where(User.username == 'admin')
            result = await session.execute(query)
            stored_hash = result.scalar_one_or_none()

            if not stored_hash:
                logger.error("❌ Admin user not found in database")
                pytest.skip("Admin user not found in database")
                return

        # Test verification with the stored hash
        is_valid = verify_password(test_password, stored_hash)
        logger.info(f"✅ Password verification test: {'Passed' if is_valid else 'Failed'}")

        if not is_valid:
            logger.warning("❌ The password 'password123' is not correct for the admin user")

        assert is_valid, "Password verification failed"
    except Exception as e:
        logger.error(f"❌ Password verification test failed: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"Password verification test failed: {str(e)}")

@pytest.mark.auth
async def test_login_function():
    """Test the login mutation directly."""
    try:
        auth = AuthMutations()
        info = MockInfo()

        # First test with admin credentials
        logger.info("Testing login with admin/password123:")
        result = await auth.login(username="admin", password="password123", info=info)

        if hasattr(result, "token"):
            logger.info("✅ Login successful!")
            logger.info(f"Token: {result.token[:20]}...")
            logger.info(f"User enabled: {result.user.enabled}")
            assert result.token, "Token should not be empty"
        else:
            logger.error(f"❌ Login failed: {result.message}")
            pytest.fail(f"Login failed: {result.message}")

    except Exception as e:
        logger.error(f"❌ Login test failed with exception: {str(e)}")
        traceback.print_exc()
        pytest.fail(f"Login test failed: {str(e)}")
