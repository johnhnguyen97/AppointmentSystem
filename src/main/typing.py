from typing import Optional, Protocol, AsyncGenerator, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

class CustomContext(Protocol):
    session: AsyncSession
    current_user: Optional[Any]
    get_current_user_override: Optional[AsyncGenerator[Any, None]]
