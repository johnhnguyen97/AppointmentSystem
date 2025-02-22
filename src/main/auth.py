from datetime import datetime, timedelta, UTC
from typing import TYPE_CHECKING, Optional
from uuid import UUID

import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from strawberry.types import Info

from src.main.config import settings

if TYPE_CHECKING:
    from src.main.typing import CustomContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(subject: str | UUID) -> str:
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
        settings.ALGORITHM
    )
    return encoded_jwt

async def check_auth(info: Info['CustomContext', None]):
    """Check if user is authenticated and return the current user"""
    current_user = None
    
    if hasattr(info.context, 'get_current_user_override'):
        current_user = await info.context.get_current_user_override()
    else:
        if not info.context.current_user:
            raise PermissionError("Not authenticated")
        current_user = info.context.current_user
        
    if not current_user:
        raise PermissionError("Not authenticated")
        
    if not current_user.enabled:
        raise PermissionError("User account is disabled")
        
    return current_user

def decode_token(token: str) -> Optional[UUID]:
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return UUID(payload.get('sub'))
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
