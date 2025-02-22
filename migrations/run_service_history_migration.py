#!/usr/bin/env python3
import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.sql import select
from ssl import create_default_context, CERT_NONE
from pathlib import Path

async def run_migration():
    # Get database URL from environment or use default
    db_url = os.getenv('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@localhost:5432/appointmentdb')
    
    # Create SSL context
    ssl_context = create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = CERT_NONE

    # Create async engine
    engine = create_async_engine(
        db_url,
        echo=True,
        pool_pre_ping=True,
        connect_args={"ssl": ssl_context}
    )

    try:
        # Read migration SQL
        migration_path = Path(__file__).parent / 'create_service_history_table.sql'
        with open(migration_path, 'r') as f:
            sql = f.read()

        # Execute migration
        async with engine.begin() as conn:
            print("Running service history table migration...")
            await conn.execute(text(sql))
            print("Migration completed successfully!")

    except Exception as e:
        print(f"Migration failed: {str(e)}")
        raise
    finally:
        await engine.dispose()

if __name__ == '__main__':
    asyncio.run(run_migration())
