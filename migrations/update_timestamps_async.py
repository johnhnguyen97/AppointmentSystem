import asyncpg
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

def convert_sqlalchemy_url(url):
    # Convert SQLAlchemy URL to asyncpg format
    # From: postgresql+asyncpg://user:pass@host:port/dbname
    # To:   postgresql://user:pass@host:port/dbname
    return url.replace('+asyncpg', '')

# Get and convert DATABASE_URL
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable is not set")
db_url = convert_sqlalchemy_url(db_url)

async def update_timestamps():
    try:
        # Connect directly using asyncpg
        conn = await asyncpg.connect(db_url)
        
        # Set default value for updated_at
        await conn.execute("""
            ALTER TABLE users 
            ALTER COLUMN updated_at SET DEFAULT now();
        """)
        print("✓ Set default value for updated_at")
        
        # Update existing NULL values
        await conn.execute("""
            UPDATE users 
            SET updated_at = now() 
            WHERE updated_at IS NULL;
        """)
        print("✓ Updated NULL values")
        
        # Ensure NOT NULL constraint
        await conn.execute("""
            ALTER TABLE users 
            ALTER COLUMN updated_at SET NOT NULL;
        """)
        print("✓ Set NOT NULL constraint")
        
        print("Migration completed successfully!")
    
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        if 'conn' in locals():
            await conn.close()

if __name__ == "__main__":
    asyncio.run(update_timestamps())
