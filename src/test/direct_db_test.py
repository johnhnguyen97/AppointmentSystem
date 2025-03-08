import asyncio
import asyncpg
import ssl

async def test_direct_connection():
    """
    Direct test using the known connection string from the Bitwarden secret
    """
    # Use the connection string directly from the Bitwarden secret 8fc2205d-8981-45d4-9f64-b29a00047d75
    db_url = "postgres://avnadmin:AVNS_IouBYATtqgwj42TCq5l@nail-appointment-db-appointmentsystem.e.aivencloud.com:23309/defaultdb"

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
        return True

    except Exception as e:
        print(f"Connection failed: {e}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_direct_connection())
    print(f"\nConnection test {'successful' if success else 'failed'}")
