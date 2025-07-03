"""
    FastAPI application main entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.routers.main_router import main_router
from app.models.database import database_manager
from app.routers.mongo_router import mongo_router
from app.routers.fetcher_router import fetcher_router
from app.services.background_tasks import start_fetcher, stop_fetcher


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
        FastAPI app startup and shutdown logic
    """

    logger.info("Starting application")

    await database_manager.connect()

    start_fetcher()
    yield

    stop_fetcher()
    await database_manager.disconnect()

    logger.info("Application stopped")


app = FastAPI(
    title="Posts Service",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(main_router)
app.include_router(mongo_router)
app.include_router(fetcher_router)