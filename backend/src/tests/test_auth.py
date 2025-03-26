import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.main.auth import verify_password, create_tokens, get_current_user
from src.main.models import User

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

async def test_admin_credentials(admin_user: User, db_session: AsyncSession):
    """Test admin user password verification."""
    async with db_session.begin():
        result = await db_session.execute(
            select(User).where(User.id == admin_user.id)
        )
        user = result.scalar_one_or_none()
        assert user is not None, "Admin user not found"

        # Verify admin password using string value
        assert verify_password("password123", str(user.password)), \
            "Password verification failed"

async def test_token_creation_and_validation(admin_user: User, db_session: AsyncSession):
    """Test token creation and validation."""
    async with db_session.begin():
        # Verify user exists
        result = await db_session.execute(
            select(User).where(User.id == admin_user.id)
        )
        user = result.scalar_one_or_none()
        assert user is not None, "Admin user not found"

        # Create tokens using string ID
        access_token, refresh_token = await create_tokens(str(user.id))
        assert access_token and isinstance(access_token, str), \
            "Access token not created"
        assert refresh_token and isinstance(refresh_token, str), \
            "Refresh token not created"

        # Verify token by getting current user
        current_user = await get_current_user(
            session=db_session,
            token=access_token
        )
        assert current_user and str(current_user.id) == str(user.id), \
            "Token validation failed"
