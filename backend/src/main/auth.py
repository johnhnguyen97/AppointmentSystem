from datetime import datetime, timedelta, UTC
from typing import TYPE_CHECKING, Optional, Any

import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from strawberry.types import Info
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.main.config import settings
from src.main.database import get_session
from src.main.models import User

if TYPE_CHECKING:
    from src.main.typing import CustomContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str) -> str:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode = {
        "exp": expire,
        "sub": str(subject)
    }
    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET_KEY,
        settings.JWT_ALGORITHM
    )
    return encoded_jwt

async def check_auth(info: Info['CustomContext', None]):
    """Check if user is authenticated and return the current user"""
    try:
        current_user = await info.context.current_user
        if not current_user:
            raise PermissionError("Not authenticated")
        if not current_user.enabled:
            raise PermissionError("User account is disabled")
        return current_user
    except Exception as e:
        raise PermissionError(str(e))

def decode_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )
        return str(payload.get('sub'))
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials"
        )

def get_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    return credentials.credentials

async def get_current_user(
    dependencies: Optional[Any] = None,
    session: Optional[AsyncSession] = None,
    token: Optional[str] = None
) -> User:
    """Get the current user from the token"""
    if not session:
        session = await get_session().__anext__()
    if not token:
        token = get_token(dependencies)
    try:
        user_id = decode_token(token)
        if not user_id:
            raise ValueError("Invalid token")

        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        user = result.scalars().first()

        if not user:
            raise ValueError("User not found")

        if not user.enabled:
            raise ValueError("User is disabled")

        return user
    except Exception as e:
        if dependencies:
            raise HTTPException(
                status_code=401,
                detail=str(e)
            )
        raise
