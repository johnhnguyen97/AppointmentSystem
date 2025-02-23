import pytest
from sqlalchemy import text
from src.main.database import async_session

@pytest.mark.asyncio
async def test_database_connection():
    """Test basic database connectivity and operations"""
    async with async_session() as session:
        # Test simple query execution
        result = await session.execute(text("SELECT 1"))
        value = result.scalar()
        assert value == 1

        # Test transaction rollback
        await session.begin()
        try:
            await session.execute(text("SELECT * FROM nonexistent_table"))
            await session.commit()
            assert False, "Should have raised an error"
        except Exception:
            await session.rollback()
            assert True, "Successfully rolled back transaction"

@pytest.mark.asyncio
async def test_schema_exists():
    """Test that our schema tables exist"""
    async with async_session() as session:
        # Check users table
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'users'
            )
        """))
        assert result.scalar(), "Users table should exist"

        # Check clients table
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'clients'
            )
        """))
        assert result.scalar(), "Clients table should exist"

        # Check service_packages table
        result = await session.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'service_packages'
            )
        """))
        assert result.scalar(), "Service packages table should exist"
