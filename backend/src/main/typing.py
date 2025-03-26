"""
Custom types and context managers for the application.
"""
from typing import Optional, TYPE_CHECKING
from fastapi import Request
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.types import Info

class CustomContext:
    """Custom context for GraphQL requests."""

    def __init__(
        self,
        session: AsyncSession,
        request: Request,
        request_id: str
    ):
        self.session = session
        self.request = request
        self.request_id = request_id
        self._current_user = None

    @property
    async def current_user(self):
        """Get the current authenticated user."""
        if not hasattr(self, '_current_user'):
            # Lazy load user from auth headers
            if TYPE_CHECKING:
                from src.main.auth import get_current_user
            else:
                from src.main.auth import get_current_user  # type: ignore
            try:
                auth_header = self.request.headers.get("Authorization")
                if auth_header and auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]
                    self._current_user = await get_current_user(
                        session=self.session,
                        token=token
                    )
                else:
                    self._current_user = None
            except Exception:
                self._current_user = None
        return self._current_user

    async def __aenter__(self):
        """Enter async context."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Exit async context."""
        if self.session:
            if exc_type is not None:
                # Rollback on error
                await self.session.rollback()
            await self.session.close()
