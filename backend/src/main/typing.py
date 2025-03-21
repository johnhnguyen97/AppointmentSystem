from typing import Any, Optional, AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from strawberry.fastapi import BaseContext
from src.main.auth import decode_token, get_current_user
import logging

logger = logging.getLogger(__name__)

class CustomContext(BaseContext):
    def __init__(
        self,
        session: AsyncSession,
        request: Optional[Request] = None,
        current_user: Optional[Any] = None,
        get_current_user_override: Optional[AsyncGenerator[Any, None]] = None
    ):
        super().__init__()
        self.session = session
        self.request = request
        self._current_user = current_user
        self.get_current_user_override = get_current_user_override

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            if exc_type is not None:
                await self.session.rollback()
            else:
                await self.session.commit()
        finally:
            await self.session.close()

    @property
    async def current_user(self) -> Optional[Any]:
        """Get the current authenticated user"""
        if self._current_user:
            return self._current_user

        if self.get_current_user_override:
            self._current_user = await self.get_current_user_override.__anext__()
            return self._current_user

        if not self.request:
            logger.error("No request object in context")
            return None

        auth_header = self.request.headers.get('Authorization')
        if not auth_header:
            logger.error("No Authorization header present")
            return None
        if not auth_header.startswith('Bearer '):
            logger.error("Authorization header does not start with 'Bearer '")
            return None

        token = auth_header.split(' ')[1]
        try:
            user_id = decode_token(token)
            if user_id:
                self._current_user = await get_current_user(None, self.session, token)
                return self._current_user
            else:
                logger.error("Token decoded but no user_id found")
        except Exception as e:
            logger.error(f"Error validating token: {str(e)}")
            raise

        return None
