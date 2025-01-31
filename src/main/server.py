from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from sqlalchemy.ext.asyncio import AsyncSession
from src.main.graphql_schema import schema
from src.main.database import engine, Base, get_session
from src.main.auth import get_current_user

# Create FastAPI app
<<<<<<< HEAD
app = FastAPI(
    title="Appointment System API",
    docs_url=None,  # Disable default Swagger UI
    redoc_url=None  # Disable ReDoc
)

# Custom startup message
import uvicorn.logging
logger = uvicorn.logging.logging.getLogger("uvicorn.info")
startup_message = """
🚀 Server running at:
   http://127.0.0.1:8000
   GraphQL endpoint: http://127.0.0.1:8000/graphql
"""
=======
app = FastAPI(title="Appointment System API")
>>>>>>> a10a25bfbcff1a280a0715f8c35eb240c0706b62

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: Configure this for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create session dependency
async def get_context(session: AsyncSession = Depends(get_session)):
    return {
        "session": session,
        "get_current_user": get_current_user
    }

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context
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
<<<<<<< HEAD
    logger.info(startup_message)
=======
>>>>>>> a10a25bfbcff1a280a0715f8c35eb240c0706b62
