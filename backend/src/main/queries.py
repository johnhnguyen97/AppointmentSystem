"""
GraphQL query definitions for the application.
"""
import strawberry
from datetime import datetime
from typing import Optional, List
from strawberry.types import Info

@strawberry.type
class SystemInfo:
    """System information type for querying server status."""
    time: str
    version: str
    environment: str
    debug_mode: bool
    database_connected: bool
    cache_enabled: bool

    @staticmethod
    def get_current() -> 'SystemInfo':
        """Get current system information."""
        from src.main.config import settings
        return SystemInfo(
            time=datetime.now().isoformat(),
            version=settings.APP_VERSION,
            environment=settings.ENVIRONMENT,
            debug_mode=settings.DEBUG,
            database_connected=True,
            cache_enabled=settings.REDIS_ENABLED
        )

@strawberry.type
class Query:
    """Root query type for the GraphQL schema."""

    @strawberry.field
    def hello(self) -> str:
        """Test query that returns a greeting."""
        return "Hello from GraphQL!"

    @strawberry.field
    def ping(self) -> str:
        """Health check query."""
        return "pong"

    @strawberry.field
    def system_info(self) -> SystemInfo:
        """Get current system information."""
        return SystemInfo.get_current()

    @strawberry.field
    def echo(self, message: str) -> str:
        """Echo back the provided message."""
        return f"You said: {message}"

    @strawberry.field
    def server_time(self) -> str:
        """Get the current server time."""
        return datetime.now().isoformat()
