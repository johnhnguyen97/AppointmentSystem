import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import colorama
from colorama import Fore, Style
from src.utils.bitwarden import get_database_credentials

# Initialize colorama for Windows
colorama.init()

async def test_connection():
    """Test connection to the database using credentials from Bitwarden"""
    print(f"{Fore.CYAN}Starting database connection test...{Style.RESET_ALL}")
    
    # Get credentials from Bitwarden using the utility function
    print(f"{Fore.CYAN}Fetching database credentials from vault...{Style.RESET_ALL}")
    try:
        db_creds = get_database_credentials()
        print(f"{Fore.GREEN}Successfully retrieved database credentials.{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}Error retrieving credentials: {str(e)}{Style.RESET_ALL}")
        raise
    
    # Construct database URL
    database_url = f"postgresql+asyncpg://{db_creds['username']}:{db_creds['password']}@{db_creds['host']}:{db_creds['port']}/{db_creds['database']}"
    
    # Print URL with cyan color (with password masked)
    masked_url = database_url.replace(db_creds['password'], '********')
    print(f"{Fore.CYAN}Attempting to connect with URL: {Style.BRIGHT}{masked_url}{Style.RESET_ALL}")
    
    engine = create_async_engine(
        database_url,
        echo=False,  # Set to False to reduce output noise
        pool_pre_ping=True
    )
    
    async_session = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False
    )

    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT version();"))
            version = result.scalar_one()
            # Success message in green
            print(f"{Fore.GREEN}Connected successfully to PostgreSQL!{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}Database version: {Style.BRIGHT}{version}{Style.RESET_ALL}")
            
    except Exception as e:
        # Error message in red
        print(f"{Fore.RED}Connection failed: {str(e)}")
        print(f"Error type: {type(e)}{Style.RESET_ALL}")
        raise
    finally:
        await engine.dispose()

if __name__ == "__main__":
    asyncio.run(test_connection())
