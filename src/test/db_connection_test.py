import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from src.main.config import settings
import colorama
from colorama import Fore, Back, Style

# Initialize colorama for Windows
colorama.init()

async def test_connection():
    # Print URL with cyan color
    print(f"{Fore.CYAN}Attempting to connect with URL: {Style.BRIGHT}{settings.DATABASE_URL}{Style.RESET_ALL}")
    
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=True,
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