import os
import ssl
from dotenv import load_dotenv

def get_database_url():
    """
    Get the database URL from environment variables or use direct string if available

    Returns:
        str: The database URL with proper formatting
    """
    # Load environment variables from .env file
    load_dotenv(override=True)

    # Check if DATABASE_URL is directly provided in the environment
    db_url = os.environ.get("DATABASE_URL")
    if db_url:
        print("Using DATABASE_URL from environment variables")
        return db_url

    # If not, construct it from components
    host = os.environ.get("DB_HOST", "localhost")
    port = os.environ.get("DB_PORT", "5432")
    database = os.environ.get("DB_NAME", "defaultdb")
    username = os.environ.get("DB_USER", "postgres")
    password = os.environ.get("DB_PASSWORD", "")

    # Ensure all required components are present
    if not all([host, port, database, username, password]):
        raise ValueError("Missing required database connection parameters")

    # Construct database URL
    db_url = f"postgres://{username}:{password}@{host}:{port}/{database}"

    return db_url

def get_ssl_context():
    """
    Create an SSL context for database connections

    Returns:
        ssl.SSLContext: A configured SSL context
    """
    # Create an SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    return ssl_context

def get_async_engine_args():
    """
    Get arguments for creating an async SQLAlchemy engine

    Returns:
        dict: Arguments for creating an async SQLAlchemy engine
    """
    args = {
        "echo": True,
        "pool_pre_ping": True,
    }

    # Only add SSL context if not in development mode
    if os.environ.get("DEVELOPMENT_MODE") != "true":
        args["connect_args"] = {
            "ssl": get_ssl_context()
        }

    return args
