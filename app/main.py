"""
FastAPI application main entry point.
"""
import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.database import database_manager
from app.routers.posts import router as posts_router
from app.services.background_tasks import periodic_fetcher

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info("Starting application")

    # Connect to database
    await database_manager.connect()

    # Start background fetcher task
    fetcher_task = asyncio.create_task(periodic_fetcher())

    yield

    # Cleanup
    fetcher_task.cancel()
    await database_manager.disconnect()
    logger.info("Application stopped")


# Create FastAPI application
app = FastAPI(
    title="Posts Service",
    version="1.0.0",
    lifespan=lifespan
)

# Include routers
app.include_router(posts_router)