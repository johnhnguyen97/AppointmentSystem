import asyncio
import asyncpg
import ssl
import sys
import os
import subprocess
from dotenv import load_dotenv

async def get_db_url_from_bws():
    """
    Get database connection URL from Bitwarden Secrets Manager
    """
    try:
        # Load environment variables from .env
        load_dotenv()

        # Get Bitwarden access token from environment
        access_token = os.environ.get("BWS_ACCESS_TOKEN")
        if not access_token:
            print("BWS_ACCESS_TOKEN not found in .env file")
            return None

        # Run the Bitwarden CLI command to get the secret
        # Make sure to escape any quotes in the access token
        cmd = ['.\\tools\\bws.exe', 'secret', 'get', '8fc2205d-8981-45d4-9f64-b29a00047d75', '--access-token', access_token]
        print(f"Executing command: {' '.join(cmd)}")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True
        )

        if result.returncode != 0:
            print(f"Error retrieving secret: {result.stderr}")
            return None

        # Parse the connection string from the output
        import json
        secret_data = json.loads(result.stdout)
        return secret_data.get("value")

    except Exception as e:
        print(f"Error accessing Bitwarden: {str(e)}")
        return None

async def test_connection():
    # Get database URL from Bitwarden or use environment variables
    db_url = await get_db_url_from_bws()

    # Fallback to environment variables if Bitwarden access fails
    if not db_url:
        print("Falling back to environment variables...")
        host = os.environ.get("DB_HOST")
        port = os.environ.get("DB_PORT")
        db_name = os.environ.get("DB_NAME")
        user = os.environ.get("DB_USER")
        password = os.environ.get("DB_PASSWORD")

        if all([host, port, db_name, user, password]):
            db_url = f"postgres://{user}:{password}@{host}:{port}/{db_name}"
            print(f"Using connection URL from environment variables (user: {user})")
        else:
            print("Database connection details not found in environment variables")
            return False

    print(f"Connecting to: {db_url.split('@')[1].split('/')[0]}")

    # Create an SSL context
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    try:
        # Connect to the database
        conn = await asyncpg.connect(db_url, ssl=ssl_context)

        print("Connection successful!")

        # Get PostgreSQL version
        version = await conn.fetchval("SELECT version()")
        print(f"PostgreSQL version: {version}")

        # List all tables in the database
        tables = await conn.fetch("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)

        if tables:
            print("\nTables in the database:")
            for record in tables:
                print(f"- {record['table_name']}")
        else:
            print("\nNo tables found in the public schema.")

        # Close the connection
        await conn.close()

    except Exception as e:
        print(f"Connection failed: {e}")
        return False

    return True

if __name__ == "__main__":
    success = asyncio.run(test_connection())
    sys.exit(0 if success else 1)
