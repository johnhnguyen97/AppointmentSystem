from typing import Optional
from fastapi import Request
from strawberry.fastapi import BaseContext
from sqlalchemy.ext.asyncio import AsyncSession
from src.main import models
from src.main.auth import get_current_user

class CustomContext(BaseContext):
    def __init__(self, session: AsyncSession, request: Request):
        super().__init__()
        self.session = session
        self.request = request

    async def get_current_user(self) -> Optional[models.User]:
        try:
            auth_header = self.request.headers.get("authorization")
            if not auth_header:
                return None
            
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return None
                
            return await get_current_user(token=token, session=self.session)
        except Exception as e:
            print(f"Auth error: {str(e)}")
            return None
