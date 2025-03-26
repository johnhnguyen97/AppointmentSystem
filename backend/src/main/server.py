"""
FastAPI server implementation with GraphQL support.
"""
import os
import uuid
import json
import logging
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
import uvicorn
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from src.main.graphql_schema import schema
from src.main.database import engine, Base, get_session
from src.main.cache import cache
from src.main.config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format=settings.LOG_FORMAT
)
logger = logging.getLogger("uvicorn.info")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# GraphQL context class
from strawberry.fastapi import BaseContext

class Context(BaseContext):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session
        self.request_id = str(uuid.uuid4())

# Context getter for GraphQL
async def get_context(session: AsyncSession = Depends(get_session)) -> Context:
    return Context(session=session)

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema,
    path="/",
    context_getter=get_context
)

# Add GraphQL router at /graphql path
app.include_router(graphql_app, prefix="/graphql")

# Redirect root to GraphQL playground
@app.get("/")
async def redirect_to_graphql():
    return RedirectResponse(url="/graphql")

# Health check endpoint
@app.get("/health")
async def health_check():
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )

# Startup event handler
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    try:
        # Create database tables
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
            logger.info("Database tables created successfully")

        # Initialize cache
        if settings.REDIS_ENABLED:
            await cache.connect()
            logger.info("Cache service initialized")
        else:
            logger.info("Using in-memory cache")

        # Log startup
        logger.info(f"Server started at http://{settings.HOST}:{settings.PORT}")
        logger.info(f"GraphQL playground available at http://{settings.HOST}:{settings.PORT}/graphql")
    except Exception as e:
        logger.error(f"Startup error: {str(e)}", exc_info=True)
        raise

# Shutdown event handler
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    try:
        if settings.REDIS_ENABLED:
            await cache.close()
        await engine.dispose()
        logger.info("Server shutdown complete")
    except Exception as e:
        logger.error(f"Shutdown error: {str(e)}", exc_info=True)
        raise
