import asyncio
import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from sqlalchemy import text
from src.main.database import engine

async def run_migration():
    async with engine.begin() as conn:
        migration_path = os.path.join(project_root, 'migrations', 'update_service_type_column.sql')
        with open(migration_path, 'r') as f:
            sql = f.read()
            await conn.execute(text(sql))

if __name__ == "__main__":
    asyncio.run(run_migration())
