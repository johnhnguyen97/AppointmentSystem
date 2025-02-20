import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

# Convert asyncpg URL to psycopg2 URL
DATABASE_URL = os.getenv('DATABASE_URL').replace('postgresql+asyncpg', 'postgresql+psycopg2')

def run_migration():
    print("Connecting to database...")
    engine = create_engine(DATABASE_URL)
    
    print("Executing migration...")
    with engine.connect() as conn:
        conn.execute(text("ALTER TABLE users ALTER COLUMN updated_at SET DEFAULT now();"))
        conn.commit()
    print("Migration completed successfully!")

if __name__ == "__main__":
    run_migration()
