# src/test/conftest.py
import pytest
import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from src.main.database import Base
from src.main.config import settings

@pytest.fixture(scope="function")
async def test_engine():
    test_db_url = settings.get_test_db_url()
    print(f"\nUsing test database URL: {test_db_url}")

    try:
        # Disable SSL verification (temporary workaround)
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE  # Disable all validation

        engine = create_async_engine(
            test_db_url,
            echo=True,
            pool_pre_ping=True,
            connect_args={
                "ssl": ssl_context
            }
        )

        # Test connection
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

        yield engine

        # Cleanup
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
        await engine.dispose()

    except Exception as e:
        print(f"Failed to connect: {str(e)}")
        raise

@pytest.fixture
async def async_session(test_engine):
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()