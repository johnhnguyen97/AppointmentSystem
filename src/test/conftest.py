import asyncio
import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.main.database import Base

import os

# Test database URL from environment variable
TEST_DATABASE_URL = os.getenv('TEST_DATABASE_URL', 'postgresql+asyncpg://localhost:5432/testdb')

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def test_engine():
    """Create a test engine instance."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=NullPool,
        echo=True  # Set to False in production
    )
    yield engine
    await engine.dispose()

@pytest.fixture(scope="function")
async def async_session(test_engine):
    """Create a fresh test database session for each test."""
    async_session = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session() as session:
        print(f"\nUsing test database URL: {TEST_DATABASE_URL}")

        # Drop all existing tables
        async with session.begin():
            await session.execute(text("DROP TABLE IF EXISTS service_history CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS service_packages CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS appointment_attendees CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS appointments CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS clients CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            await session.execute(text("DROP TYPE IF EXISTS appointmentstatus CASCADE;"))
            await session.execute(text("DROP TYPE IF EXISTS servicetype CASCADE;"))
            await session.execute(text("DROP SEQUENCE IF EXISTS user_sequential_id_seq;"))

            # Create sequence
            await session.execute(text("CREATE SEQUENCE user_sequential_id_seq;"))

            # Create enum types
            await session.execute(text("""
                CREATE TYPE appointmentstatus AS ENUM (
                    'SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'DECLINED'
                );
            """))

            await session.execute(text("""
                CREATE TYPE servicetype AS ENUM (
                    'HAIRCUT', 'MANICURE', 'PEDICURE', 'FACIAL', 'MASSAGE',
                    'HAIRCOLOR', 'HAIRSTYLE', 'MAKEUP', 'WAXING', 'OTHER'
                );
            """))

            # Create tables in correct order
            await session.execute(text("""
                CREATE TABLE users (
                    id UUID PRIMARY KEY,
                    sequential_id INTEGER DEFAULT nextval('user_sequential_id_seq') UNIQUE,
                    username VARCHAR UNIQUE,
                    email VARCHAR UNIQUE,
                    password VARCHAR,
                    first_name VARCHAR,
                    last_name VARCHAR,
                    enabled BOOLEAN DEFAULT true,
                    is_admin BOOLEAN DEFAULT false,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))

            await session.execute(text("""
                CREATE TABLE clients (
                    id UUID PRIMARY KEY,
                    phone VARCHAR(20) NOT NULL,
                    service servicetype NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    notes VARCHAR(500),
                    category VARCHAR(20) NOT NULL DEFAULT 'NEW',
                    loyalty_points INTEGER NOT NULL DEFAULT 0,
                    referred_by UUID REFERENCES clients(id),
                    user_id UUID UNIQUE REFERENCES users(id),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))

            await session.execute(text("""
                CREATE TABLE appointments (
                    id UUID PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    description VARCHAR(500),
                    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    end_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    status appointmentstatus NOT NULL DEFAULT 'SCHEDULED',
                    service_type servicetype NOT NULL,
                    buffer_time INTEGER NOT NULL DEFAULT 0,
                    is_recurring BOOLEAN NOT NULL DEFAULT false,
                    recurrence_pattern VARCHAR(20),
                    creator_id UUID REFERENCES users(id) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))

            await session.execute(text("""
                CREATE TABLE appointment_attendees (
                    user_id UUID REFERENCES users(id),
                    appointment_id UUID REFERENCES appointments(id),
                    PRIMARY KEY (user_id, appointment_id)
                );
            """))

            await session.execute(text("""
                CREATE TABLE service_packages (
                    id UUID PRIMARY KEY,
                    client_id UUID REFERENCES clients(id) NOT NULL,
                    service_type servicetype NOT NULL,
                    total_sessions INTEGER NOT NULL,
                    sessions_remaining INTEGER NOT NULL,
                    purchase_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    expiry_date TIMESTAMP WITH TIME ZONE NOT NULL,
                    package_cost FLOAT NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))

            await session.execute(text("""
                CREATE TABLE service_history (
                    id UUID PRIMARY KEY,
                    client_id UUID REFERENCES clients(id) NOT NULL,
                    service_type servicetype NOT NULL,
                    provider_name VARCHAR NOT NULL,
                    date_of_service TIMESTAMP WITH TIME ZONE NOT NULL,
                    notes VARCHAR(500),
                    service_cost FLOAT,
                    loyalty_points_earned INTEGER NOT NULL DEFAULT 0,
                    points_redeemed INTEGER NOT NULL DEFAULT 0,
                    package_id UUID REFERENCES service_packages(id),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """))

        yield session

    # Clean up tables after each test
    async with async_session() as session:
        async with session.begin():
            await session.execute(text("DROP TABLE IF EXISTS service_history CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS service_packages CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS appointment_attendees CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS appointments CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS clients CASCADE;"))
            await session.execute(text("DROP TABLE IF EXISTS users CASCADE;"))
            await session.execute(text("DROP TYPE IF EXISTS appointmentstatus CASCADE;"))
            await session.execute(text("DROP TYPE IF EXISTS servicetype CASCADE;"))
            await session.execute(text("DROP SEQUENCE IF EXISTS user_sequential_id_seq;"))
