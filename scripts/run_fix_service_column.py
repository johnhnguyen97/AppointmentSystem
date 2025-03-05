"""
Script to execute the fix_service_column.sql script
"""
import asyncio
import sys
import os
import ssl

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

# Create an SSL context that doesn't verify the certificate
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Import database configuration from the project
from src.main.config import settings

# Create a database connection using the configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    pool_pre_ping=True,
    connect_args={
        "ssl": ssl_context
    }
)

async def run_sql_script():
    """Run the SQL script to fix the service column type"""
    # Read the SQL script
    script_path = os.path.join(os.path.dirname(__file__), 'fix_service_column.sql')
    with open(script_path, 'r') as f:
        sql_script = f.read()

    # Split the SQL script into individual statements
    statements = []
    current_statement = []
    for line in sql_script.splitlines():
        line = line.strip()
        if not line or line.startswith('--'):
            continue

        current_statement.append(line)
        if line.endswith(';'):
            statements.append(' '.join(current_statement))
            current_statement = []

    # Execute each statement separately
    async with engine.begin() as conn:
        print("Executing SQL script...")
        for i, statement in enumerate(statements):
            if statement.strip():
                print(f"Executing statement {i+1}/{len(statements)}: {statement[:50]}...")
                await conn.execute(text(statement))
        print("SQL script executed successfully!")

if __name__ == '__main__':
    asyncio.run(run_sql_script())
