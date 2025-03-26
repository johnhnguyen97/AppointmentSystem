"""
Authentication and authorization implementation.
"""
from datetime import datetime, timedelta, UTC
import time
from enum import Enum
from typing import TYPE_CHECKING, Optional, Any, List, Type, Tuple
import jwt
from fastapi import HTTPException, Security, Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from strawberry.types import Info
from strawberry.permission import BasePermission
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from src.main.config import settings
from src.main.database import get_session
from src.main.models import User
from src.main.cache import RedisCache

if TYPE_CHECKING:
    from src.main.typing import CustomContext

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()
cache = RedisCache()

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

class Role(str, Enum):
    ADMIN = "admin"
    STAFF = "staff"
    USER = "user"

class IsAuthenticated(BasePermission):
    """Permission that only allows authenticated users."""
    message = "User is not authenticated"

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        try:
            user = await info.context.current_user
            if not user:
                return False

            # Get fresh user data to verify status
            session = info.context.session
            user_status = await session.scalar(
                select(User.enabled).where(User.id == user.id)
            )
            return user_status is True
        except Exception as e:
            logger.error(f"Authentication check error: {str(e)}")
            return False

class BaseRolePermission(BasePermission):
    """Base class for role-based permissions."""
    message = "Invalid permission configuration"

    def __init__(self, required_roles: List[Role]):
        self.required_roles = required_roles
        super().__init__()

    async def has_permission(self, source: Any, info: Info, **kwargs) -> bool:
        try:
            user = await info.context.current_user
            if not user:
                return False

            # Get fresh user data with role status and store results
            session = info.context.session
            status_result = await session.execute(
                select(User.enabled, User.is_admin, User.is_staff)
                .where(User.id == user.id)
            )
            user_status = status_result.one_or_none()
            if not user_status or not user_status.enabled:
                return False

            if await user_status.is_admin:  # Admin has all permissions
                return True

            if Role.STAFF in self.required_roles and await user_status.is_staff:
                return True

            if Role.USER in self.required_roles:
                return True

            return False
        except Exception as e:
            logger.error(f"Permission check error: {str(e)}")
            return False

def role_required(role: Role) -> Type[BasePermission]:
    """Create a permission class for a single role."""
    class SingleRolePermission(BaseRolePermission):
        message = f"User must have {role.value} role"

        def __init__(self):
            super().__init__([role])

    return SingleRolePermission

def roles_required(roles: List[Role]) -> Type[BasePermission]:
    """Create a permission class for multiple roles."""
    class MultiRolePermission(BaseRolePermission):
        message = f"User must have one of these roles: {[r.value for r in roles]}"

        def __init__(self):
            super().__init__(roles)

    return MultiRolePermission

def get_password_hash(password: str) -> str:
    """Hash a password for storing."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a stored password against a provided password."""
    return pwd_context.verify(plain_password, hashed_password)

async def create_token(subject: str, token_type: TokenType) -> str:
    """Create a JWT token."""
    try:
        if token_type == TokenType.ACCESS:
            expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
            expire = datetime.now(UTC) + timedelta(minutes=expire_minutes)
            expire_seconds = expire_minutes * 60
        else:
            expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS
            expire = datetime.now(UTC) + timedelta(days=expire_days)
            expire_seconds = expire_days * 24 * 60 * 60

        to_encode = {
            "exp": expire,
            "iat": datetime.now(UTC),
            "sub": str(subject),
            "type": token_type
        }
        encoded_jwt = jwt.encode(
            to_encode,
            settings.JWT_SECRET_KEY,
            settings.JWT_ALGORITHM
        )

        # Store token in cache for blacklist checking with proper expiration
        cache_key = f"token:{token_type}:{encoded_jwt}"
        try:
            await cache.set(
                cache_key,
                "valid",
                expire_in=expire_seconds
            )
        except Exception as e:
            logger.error(f"Failed to store token in cache: {str(e)}")
            # Continue even if cache fails - token will still work but can't be revoked

        return encoded_jwt
    except Exception as e:
        logger.error(f"Token creation failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to create authentication token"
        )

async def create_tokens(user_id: str) -> Tuple[str, str]:
    """Create both access and refresh tokens."""
    access_token = await create_token(user_id, TokenType.ACCESS)
    refresh_token = await create_token(user_id, TokenType.REFRESH)
    return access_token, refresh_token

async def revoke_token(token: str, token_type: TokenType):
    """Revoke a token by adding it to blacklist cache."""
    cache_key = f"token:{token_type}:{token}"
    await cache.delete(cache_key)

def is_token_valid(token: str, token_type: TokenType) -> bool:
    """Check if a token is valid (not revoked)."""
    cache_key = f"token:{token_type}:{token}"
    return bool(cache.get(cache_key))

def decode_token(token: str) -> Optional[str]:
    """Decode and validate a JWT token."""
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET_KEY,
            algorithms=[settings.JWT_ALGORITHM]
        )

        # Check if token is revoked
        token_type = TokenType(payload.get('type', TokenType.ACCESS))
        if not is_token_valid(token, token_type):
            raise jwt.InvalidTokenError("Token has been revoked")

        return str(payload.get('sub'))
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=401,
            detail=str(e)
        )

def get_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    """Extract token from authorization header."""
    return credentials.credentials

async def get_current_user(
    dependencies: Optional[HTTPAuthorizationCredentials] = None,
    session: Optional[AsyncSession] = None,
    token: Optional[str] = None
) -> User:
    """Get the current user from the token with caching."""
    try:
        if not session:
            session = await anext(get_session())
        if not token and dependencies:
            token = get_token(dependencies)
        if not token:
            raise ValueError("No token provided")

        user_id = decode_token(token)
        if not user_id:
            raise ValueError("Invalid token")

        # Try to get user from cache first
        cache_key = f"user:{user_id}"
        cached_user = None
        try:
            cached_data = cache.get(cache_key)
            if cached_data and isinstance(cached_data, User):
                # Verify user still exists and is enabled
                db_user = await session.get(User, cached_data.id)
                if db_user:
                    enabled_check = await session.scalar(select(User.enabled).where(User.id == db_user.id))
                    if enabled_check:
                        cached_user = cached_data
                    else:
                        result = await cache.delete(cache_key)
                        if not result:
                            logger.warning(f"Failed to delete cache key: {cache_key}")
        except Exception as e:
            logger.error(f"Cache error in get_current_user: {str(e)}")

        if cached_user:
            return cached_user

        # Get from database and store result
        stmt = select(User).where(User.id == user_id)
        user_result = await session.execute(stmt)
        user = user_result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        # Check if user is enabled using scalar
        user_enabled = await session.scalar(
            select(User.enabled).where(User.id == user.id)
        )
        if not user_enabled:
            raise ValueError("User account is disabled")

        # Cache user for future requests
        try:
            await cache.set(
                cache_key,
                user,
                expire_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        except Exception as e:
            logger.error(f"Failed to cache user: {str(e)}")

        return user

    except Exception as e:
        if dependencies:
            raise HTTPException(
                status_code=401,
                detail=str(e)
            )
        raise

async def check_rate_limit(info: Info['CustomContext', None]) -> None:
    """Check rate limiting for the current user/IP."""
    try:
        request = info.context.request
        if not request or not request.client:
            logger.warning("No request or client information available for rate limiting")
            return

        # Use user ID if authenticated
        user = await info.context.current_user
        client_id = str(user.id) if user else request.client.host
        key = f"rate_limit:{client_id}"

        try:
            # Simple rate limiting without Redis-specific operations
            current_count = await cache.get(key)
            count = int(current_count) if current_count else 0

            # Always set/update the key with 60 second expiry
            count += 1
            await cache.set(key, str(count), expire_in=60)  # 1 minute window

            if count > settings.RATE_LIMIT_PER_MINUTE:
                current_time = int(time.time())
                window_end = (current_time // 60 + 1) * 60
                remaining = window_end - current_time
                raise HTTPException(
                    status_code=429,
                    detail=f"Rate limit exceeded. Try again in {remaining} seconds."
                )

        except HTTPException:
            raise
        except Exception as cache_error:
            logger.error(f"Rate limit cache error: {str(cache_error)}")
            # Continue if cache fails
            return
    except Exception as e:
        logger.error(f"Rate limit error: {str(e)}")

async def check_auth(info: Info['CustomContext', None]) -> User:
    """Check if user is authenticated with rate limiting."""
    await check_rate_limit(info)

    try:
        current_user = await info.context.current_user
        if not current_user:
            raise PermissionError("Not authenticated")

        # Get fresh user data to verify status
        session = info.context.session
        user_status = await session.execute(
            select(User, User.enabled)
            .where(User.id == current_user.id)
        )
        result = user_status.one_or_none()

        if not result:
            raise PermissionError("User not found")

        user, enabled = result
        if not enabled:
            raise PermissionError("User account is disabled")

        return user
    except Exception as e:
        raise PermissionError(str(e))
