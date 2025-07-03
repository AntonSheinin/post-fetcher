"""
FastAPI application main entry point.
"""
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.models.database import database_manager
from app.services.background_tasks import start_fetcher, stop_fetcher

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
    start_fetcher()

    yield

    # Cleanup
    stop_fetcher()
    await database_manager.disconnect()
    logger.info("Application stopped")


# Create FastAPI application
app = FastAPI(
    title="Posts Service",
    version="1.0.0",
    lifespan=lifespan
)

# Include all routers
from app.routers.posts import main_router, mongo_router, fetcher_router

app.include_router(main_router)
app.include_router(mongo_router)
app.include_router(fetcher_router)