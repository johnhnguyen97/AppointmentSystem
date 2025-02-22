# src/test/conftest.py
import pytest
import os
import ssl
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text
from src.main.database import Base
from src.main.config import settings

@pytest.fixture(scope="function")
async def test_engine():
    test_db_url = settings.get_test_db_url()
    print(f"\nUsing test database URL: {test_db_url}")

    try:
        # Create SSL context with more permissive settings
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        engine = create_async_engine(
            test_db_url,
            echo=True,
            pool_pre_ping=True,
            connect_args={
                "ssl": ssl_context
            }
        )

        # Drop all tables and sequences, then recreate them
        async with engine.begin() as conn:
            # Drop everything first
            await conn.run_sync(Base.metadata.drop_all)
            # Drop everything in correct order
            await conn.execute(text("DROP TABLE IF EXISTS service_history CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS appointment_attendees CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS appointments CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS clients CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            await conn.execute(text("DROP TYPE IF EXISTS appointmentstatus CASCADE"))
            await conn.execute(text("DROP SEQUENCE IF EXISTS user_sequential_id_seq"))

            # Import models to ensure they're registered with the metadata
            from src.main.models import User, Client, Appointment
            
            # Create sequence, enum type, and tables all in one transaction
            await conn.execute(text("CREATE SEQUENCE user_sequential_id_seq"))
            await conn.execute(text("""
                CREATE TYPE appointmentstatus AS ENUM 
                ('SCHEDULED', 'CONFIRMED', 'CANCELLED', 'COMPLETED', 'DECLINED')
            """))
            
            # Create tables with proper DDL statements
            await conn.execute(text("""
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
                )
            """))

            await conn.execute(text("""
                CREATE TABLE clients (
                    id UUID PRIMARY KEY,
                    phone VARCHAR(20) NOT NULL,
                    service VARCHAR NOT NULL,
                    status VARCHAR(20) NOT NULL DEFAULT 'active',
                    notes VARCHAR(500),
                    user_id UUID UNIQUE REFERENCES users(id)
                )
            """))

            await conn.execute(text("""
                CREATE TABLE appointments (
                    id UUID PRIMARY KEY,
                    title VARCHAR(100) NOT NULL,
                    description VARCHAR(500),
                    start_time TIMESTAMP WITH TIME ZONE NOT NULL,
                    duration_minutes INTEGER NOT NULL,
                    status appointmentstatus NOT NULL DEFAULT 'SCHEDULED',
                    creator_id UUID REFERENCES users(id) NOT NULL,
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))

            await conn.execute(text("""
                CREATE TABLE appointment_attendees (
                    user_id UUID REFERENCES users(id),
                    appointment_id UUID REFERENCES appointments(id),
                    PRIMARY KEY (user_id, appointment_id)
                )
            """))

            await conn.execute(text("""
                CREATE TABLE service_history (
                    id UUID PRIMARY KEY,
                    client_id UUID REFERENCES clients(id) NOT NULL,
                    service_type VARCHAR NOT NULL,
                    provider_name VARCHAR NOT NULL,
                    date_of_service TIMESTAMP WITH TIME ZONE NOT NULL,
                    notes VARCHAR(500),
                    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """))

        yield engine

        # Cleanup
        async with engine.begin() as conn:
            await conn.execute(text("DROP TABLE IF EXISTS appointment_attendees CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS appointments CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS clients CASCADE"))
            await conn.execute(text("DROP TABLE IF EXISTS users CASCADE"))
            await conn.execute(text("DROP SEQUENCE IF EXISTS user_sequential_id_seq"))
            await conn.execute(text("DROP TYPE IF EXISTS appointmentstatus CASCADE"))
        await engine.dispose()

    except Exception as e:
        print(f"Failed to connect: {str(e)}")
        raise

@pytest.fixture
async def db_session(test_engine):
    async_session_maker = sessionmaker(
        test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    async with async_session_maker() as session:
        yield session
        await session.rollback()

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
