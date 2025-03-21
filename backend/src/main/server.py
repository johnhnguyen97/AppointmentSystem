from typing import Optional
from fastapi import FastAPI, Depends
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from strawberry.types import Info
from sqlalchemy.ext.asyncio import AsyncSession
from src.main.graphql_schema import schema
from src.main.database import engine, Base, get_session
from src.main.typing import CustomContext

# Create FastAPI app
app = FastAPI(
    title="Appointment System API",
    docs_url=None,  # Disable default Swagger UI
    redoc_url=None  # Disable ReDoc
)

import os
import uvicorn.logging

# Get port from environment or use default
PORT = int(os.environ.get("PORT", "8080"))
HOST = os.environ.get("HOST", "127.0.0.1")

logger = uvicorn.logging.logging.getLogger("uvicorn.info")
startup_message = f"""
🚀 Server running at:
   http://{HOST}:{PORT}
   GraphQL endpoint: http://{HOST}:{PORT}/graphql
"""

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:4200",  # Angular dev server
        "http://127.0.0.1:4200"   # Alternative Angular URL
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create GraphQL router with context
async def get_context(
    request: Request,
    session: AsyncSession = Depends(get_session)
) -> CustomContext:
    logger.info(f"GraphQL request received: {request.url}")
    context = CustomContext(session=session, request=request)
    return await context.__aenter__()

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
    graphiql=True  # Enable GraphiQL interface for testing
)

# Add GraphQL endpoint
app.include_router(graphql_app, prefix="/graphql")

# Add health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Startup event to create database tables
@app.on_event("startup")
async def startup_event():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info(startup_message)

if __name__ == "__main__":
    uvicorn.run(
        "src.main.server:app",
        host=HOST,
        port=PORT,
        reload=True
    )
