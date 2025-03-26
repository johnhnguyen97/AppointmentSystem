import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = [pytest.mark.asyncio, pytest.mark.integration]

async def test_database_engine_connection(db_session: AsyncSession):
    """Test database connection using engine."""
    async with db_session.begin():
        result = await db_session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1, "Database connection failed"

async def test_database_session(db_session: AsyncSession):
    """Test database connection using session."""
    async with db_session.begin():
        result = await db_session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1, "Session connection failed"
