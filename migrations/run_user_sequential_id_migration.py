import asyncio
import asyncpg
import os
import sys

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

from src.main.config import settings

async def run_migration():
    # Get database URL from settings
    db_url = settings.DATABASE_URL
    if db_url.startswith('postgresql+asyncpg://'):
        db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
    
    # Connect to the database
    conn = await asyncpg.connect(db_url)

    try:
        # Read and execute the migration SQL
        with open('migrations/add_user_sequential_id.sql', 'r') as f:
            migration_sql = f.read()
            
        print("Running user sequential ID migration...")
        await conn.execute(migration_sql)
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {str(e)}")
        raise
    finally:
        await conn.close()

if __name__ == "__main__":
    asyncio.run(run_migration())
