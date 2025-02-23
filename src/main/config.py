from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

    DATABASE_URL: str
    TEST_DATABASE_URL: Optional[str] = None
    PASSWORD_MIN_LENGTH: int = 8
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Rate limiting
    RATE_LIMIT_PER_MINUTE: int = 60
    
    # Add logging configuration
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    

    def get_test_db_url(self) -> str:
        """Get test database URL with correct format"""
        base_url = self.TEST_DATABASE_URL or self.DATABASE_URL

        if not base_url:
            raise ValueError("DATABASE_URL must be set in the environment or .env file")

        # Ensure correct prefix
        if base_url.startswith('postgres://'):
            base_url = base_url.replace('postgres://', 'postgresql+asyncpg://', 1)

        # Replace default database name with test database if no TEST_DATABASE_URL is provided
        if self.TEST_DATABASE_URL is None and 'defaultdb' in base_url:
            base_url = base_url.replace('defaultdb', 'testdb')

        # Remove SSL parameters from the URL (asyncpg uses an SSL context)
        base_url = base_url.split('?')[0]

        return base_url  # Do NOT append `?sslmode=require`

settings = Settings()
