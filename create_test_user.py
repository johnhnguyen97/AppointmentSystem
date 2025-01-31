import asyncio
from sqlalchemy import select
from src.main.database import engine, Base
from src.main.models import User
from src.main.auth import get_password_hash
from uuid import uuid4

async def create_test_user():
    async with engine.begin() as conn:
        # Create tables if they don't exist
        await conn.run_sync(Base.metadata.create_all)
    
    async with engine.connect() as conn:
        # Create a test user
        test_user = User(
            id=uuid4(),
            username="testuser",
            email="test@example.com",
            password=get_password_hash("testpass123"),
            first_name="Test",
            last_name="User",
            enabled=True
        )
        
        await conn.execute(
            User.__table__.insert().values(
                id=test_user.id,
                username=test_user.username,
                email=test_user.email,
                password=test_user.password,
                first_name=test_user.first_name,
                last_name=test_user.last_name,
                enabled=test_user.enabled
            )
        )
        await conn.commit()
        
        # Verify user was created
        result = await conn.execute(
            select(User).where(User.username == "testuser")
        )
        user = result.first()
        if user:
            print(f"Test user created successfully!")
            print(f"Username: testuser")
            print(f"Password: testpass123")
        else:
            print("Failed to create test user")

if __name__ == "__main__":
    asyncio.run(create_test_user())
