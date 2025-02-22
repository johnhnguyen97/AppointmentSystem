from typing import Optional, AsyncGenerator, Any
from sqlalchemy.ext.asyncio import AsyncSession

class CustomContext:
    def __init__(
        self,
        session: AsyncSession,
        current_user: Optional[Any] = None,
        get_current_user_override: Optional[AsyncGenerator[Any, None]] = None
    ):
        self.session = session
        self.current_user = current_user
        self.get_current_user_override = get_current_user_override
