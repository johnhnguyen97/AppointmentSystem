from sqlalchemy.ext.asyncio import AsyncSession
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from .models import User

class CustomContextDict(dict):
    session: Optional[AsyncSession]
    user: Optional['User']
    token: Optional[str]
