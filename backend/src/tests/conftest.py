"""Test fixtures and configuration."""
import asyncio
import datetime
import platform
import sys
from typing import AsyncGenerator

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.sql import text

from src.main.auth import get_password_hash
from src.main.config import settings
from src.main.database import Base
from src.main.models import User

# Test database configuration
test_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=True,
    future=True,
    pool_pre_ping=True
)

test_async_session_factory = async_sessionmaker(
    test_engine,
    expire_on_commit=False,
    class_=AsyncSession
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an event loop for each test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest_asyncio.fixture(scope="function")
async def db_session(event_loop: asyncio.AbstractEventLoop) -> AsyncGenerator[AsyncSession, None]:
    """Create a fresh database session for each test."""
    async with test_async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

@pytest_asyncio.fixture(scope="function")
async def admin_user(db_session: AsyncSession) -> User:
    """Create and return an admin user for testing."""
    import uuid
    unique_id = str(uuid.uuid4())[:8]

    admin = User(**{
        "id": f"admin_test_{unique_id}",
        "username": f"admin_{unique_id}",
        "email": f"admin_{unique_id}@example.com",
        "password": get_password_hash("password123"),
        "is_admin": True,
        "first_name": "Admin",
        "last_name": "User",
        "enabled": True
    })

    db_session.add(admin)
    await db_session.commit()
    await db_session.refresh(admin)
    return admin

def pytest_html_report_title(report):
    """Customize the HTML report title."""
    report.title = "Appointment System Test Report"

def pytest_configure(config):
    """Add custom markers and environment info."""
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "api: mark test as an API test"
    )

def pytest_html_results_table_header(cells):
    """Customize the results table header."""
    cells.insert(2, "<th>Time</th>")
    cells.insert(3, "<th>Category</th>")

def pytest_html_results_table_row(report, cells):
    """Customize the results table rows."""
    cells.insert(2, f"<td>{datetime.datetime.now().strftime('%H:%M:%S')}</td>")
    cells.insert(3, f"<td>{getattr(report, 'category', 'N/A')}</td>")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Customize test result reporting."""
    outcome = yield
    report = outcome.get_result()

    # Add test category based on markers
    test_fn = item.function
    category = None

    if any(mark.name == 'integration' for mark in item.iter_markers()):
        category = 'Integration'
    elif any(mark.name == 'api' for mark in item.iter_markers()):
        category = 'API'
    else:
        category = 'Unit'

    report.category = category

def pytest_html_results_summary(prefix, summary, postfix):
    """Add custom summary section to the report."""
    prefix.extend([
        "<div class='summary'>",
        "<div class='summary-item'>",
        f"<div>Python Version: {platform.python_version()}</div>",
        "</div>",
        "<div class='summary-item'>",
        f"<div>Platform: {platform.platform()}</div>",
        "</div>",
        "<div class='summary-item'>",
        f"<div>Test Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>",
        "</div>",
        "</div>"
    ])
