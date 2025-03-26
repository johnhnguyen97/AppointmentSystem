"""
Application configuration settings.
"""
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from urllib.parse import urlparse, parse_qs

class Settings(BaseSettings):
    """Application settings with environment variable support."""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        validate_default=True,
        env_prefix="",
        case_sensitive=True
    )

    # Server
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    WORKERS: int = 1

    # Database
    DATABASE_URL: str = Field(
        default=...,  # Makes the field required
        validation_alias='DATABASE_URL',
        description="PostgreSQL database connection URL"
    )
    TEST_DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False

    @field_validator("DATABASE_URL")
    def validate_database_url(cls, v: str) -> str:
        """Validate and normalize database URL."""
        if not v:
            raise ValueError("DATABASE_URL must not be empty")

        try:
            parsed = urlparse(v)
            # Ensure proper scheme for asyncpg
            if parsed.scheme not in ("postgresql", "postgresql+asyncpg"):
                v = v.replace("postgresql://", "postgresql+asyncpg://", 1)

            # Verify required components
            if not all([parsed.username, parsed.password, parsed.hostname, parsed.path]):
                raise ValueError("Database URL must include username, password, host, and database name")

            return v
        except Exception as e:
            raise ValueError(f"Invalid database URL format: {str(e)}")

    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_ENABLED: bool = False
    REDIS_MAX_CONNECTIONS: int = 10
    REDIS_SOCKET_TIMEOUT: int = 5
    REDIS_SOCKET_CONNECT_TIMEOUT: int = 5

    # Auth
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 72
    JWT_SECRET_KEY: str = Field(default="development-secret-key-change-me", alias="JWT_SECRET_KEY")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TOKEN_URL: str = "/auth/token"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:4200",  # Angular dev server
        "http://127.0.0.1:4200",
        "http://localhost:8000",
        "http://127.0.0.1:8000"
    ]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_BURST: int = 100
    RATE_LIMIT_ENABLED: bool = True

    # Security
    SECURITY_PASSWORD_SALT: str = Field(
        default="change-me-in-production",
        alias="SECURITY_PASSWORD_SALT"
    )
    SECURITY_ALGORITHM: str = "pbkdf2_sha512"
    SECURITY_PASSWORD_HASH: str = "bcrypt"
    SECURITY_PASSWORD_ITERATIONS: int = 100_000

    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE: Optional[str] = None
    LOG_ROTATION: str = "20 MB"
    LOG_RETENTION: str = "14 days"

    # Application
    DEBUG: bool = False
    TESTING: bool = False
    APP_NAME: str = "Appointment System"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    SECRET_KEY: str = Field(
        default="dev-secret-key-change-me",
        alias="SECRET_KEY"
    )

    def get_test_db_url(self) -> str:
        """Get test database URL with correct format."""
        base_url = self.TEST_DATABASE_URL or self.DATABASE_URL
        if not base_url:
            raise ValueError("DATABASE_URL must be set")

        parsed = urlparse(base_url)
        # Ensure correct prefix for async driver
        if parsed.scheme == "postgresql":
            base_url = base_url.replace("postgresql://", "postgresql+asyncpg://", 1)

        # Replace database name for test database
        if self.TEST_DATABASE_URL is None and "defaultdb" in base_url:
            base_url = base_url.replace("defaultdb", "testdb")

        return base_url

    def get_server_url(self) -> str:
        """Get the complete server URL."""
        return f"http://{self.HOST}:{self.PORT}"

# Create settings instance
settings = Settings()

# Export settings instance
__all__ = ["settings"]
