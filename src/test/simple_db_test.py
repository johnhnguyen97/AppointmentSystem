import asyncio
import asyncpg
from src.utils.db_connection import get_database_url, get_ssl_context

async def test_db_connection():
    """
    Simple test to verify database connection using environment variables
    """
    # Get the database URL from environment variables
    db_url = get_database_url()
    print(f"Connecting to: {db_url.split('@')[1].split('/')[0]}")

    # Get SSL context
    ssl_context = get_ssl_context()

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
        return True
    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_db_connection())
    print(f"\nConnection test {'successful' if success else 'failed'}")
