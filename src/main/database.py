# src/main/database.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from .config import settings
import ssl  # <-- Add this import

# Create Base class
Base = declarative_base()

def create_database_url(url: str) -> str:
    """Ensure the database URL uses the correct dialect name"""
    if url.startswith('postgres://'):
        return url.replace('postgres://', 'postgresql+asyncpg://', 1)
    return url

# Create async engine
engine = create_async_engine(
    create_database_url(settings.DATABASE_URL),
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "ssl": ssl.create_default_context(cafile="certs/ca.pem")  # Path adjusted
    }
)

# Create async session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)