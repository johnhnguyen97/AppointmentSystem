import asyncio
import json
import os
import subprocess
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
import colorama
from colorama import Fore, Style

# Initialize colorama for Windows
colorama.init()

def get_db_credentials_from_bitwarden():
    """Get database credentials from Bitwarden vault"""
    try:
        # Get API key credentials from environment variables
        client_id = os.environ.get("BW_CLIENTID")
        client_secret = os.environ.get("BW_CLIENTSECRET")
        
        # If environment variables are not available, use hardcoded values
        if not client_id or not client_secret:
            print(f"{Fore.YELLOW}Warning: Environment variables not found, using hardcoded values{Style.RESET_ALL}")
            # Use the values from the image provided
            client_id = "user.dca9ef89-fcc0-41e2-89d9-afba01346960"
            client_secret = "PWt6CE7h6q80Y73ICJxqbrLrHho6zs"
        
        print(f"{Fore.CYAN}Using Bitwarden credentials - ID: {client_id[:10]}...{Style.RESET_ALL}")
        
        # Set environment variables for Bitwarden API
        env = os.environ.copy()
        env["BW_CLIENTID"] = client_id
        env["BW_CLIENTSECRET"] = client_secret
        
        # Login with API key
        print(f"{Fore.CYAN}Logging in to Bitwarden with API key...{Style.RESET_ALL}")
        login_result = subprocess.run(
            ['bw', 'login', '--apikey', '--raw'],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        
        # Get session key
        session_key = login_result.stdout.strip()
        print(f"{Fore.CYAN}Successfully logged in to Bitwarden.{Style.RESET_ALL}")
        
        # Get the Nail Appointment Database item
        print(f"{Fore.CYAN}Fetching database credentials from vault...{Style.RESET_ALL}")
        result = subprocess.run(
            ['bw', 'get', 'item', 'Nail Appointment Database', '--session', session_key],
            capture_output=True,
            text=True,
            env=env,
            check=True
        )
        
        # Parse the JSON output
        item = json.loads(result.stdout)
        
        # Extract credentials
        # TODO: Update this section to match the actual structure of your Bitwarden item
        credentials = {}
        for field in item.get('fields', []):
            if field.get('name') == 'username':
                credentials['username'] = field.get('value')
            elif field.get('name') == 'password':
                credentials['password'] = field.get('value')
        
        # Get additional fields from the item
        login_data = item.get('login', {})
        if 'username' in login_data:
            credentials['username'] = login_data.get('username')
        if 'password' in login_data:
            credentials['password'] = login_data.get('password')
        
        # Get custom fields if needed
        for field in item.get('fields', []):
            if field.get('name') == 'host':
                credentials['host'] = field.get('value')
            elif field.get('name') == 'port':
                credentials['port'] = field.get('value')
            elif field.get('name') == 'database':
                credentials['database'] = field.get('value')
        
        # Set defaults if not found
        credentials.setdefault('host', 'localhost')
        credentials.setdefault('port', '5432')
        credentials.setdefault('database', 'appointment_system')
        
        return credentials
        
    except subprocess.CalledProcessError as e:
        print(f"{Fore.RED}Bitwarden CLI error: {e.stderr}{Style.RESET_ALL}")
        raise
    except json.JSONDecodeError:
        print(f"{Fore.RED}Failed to parse Bitwarden output as JSON{Style.RESET_ALL}")
        raise
    except Exception as e:
        print(f"{Fore.RED}Error retrieving credentials: {str(e)}{Style.RESET_ALL}")
        raise

async def test_connection():
    """Test connection to the database using credentials from Bitwarden"""
    print(f"{Fore.CYAN}Starting database connection test...{Style.RESET_ALL}")
    
    # Get credentials from Bitwarden
    db_creds = get_db_credentials_from_bitwarden()
    
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
