"""
    FastAPI application main entry point.
"""

import logging
from dotenv import load_dotenv
from contextlib import asynccontextmanager

from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, Depends, HTTPException

from app.routers.auth_router import auth_router
from app.routers.main_router import main_router
from app.models.database import database_manager
from app.routers.mongo_router import mongo_router
from app.routers.fetcher_router import fetcher_router
from app.services.background_tasks import start_fetcher, stop_fetcher


load_dotenv()

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
    description="API with JWT authentication",
    lifespan=lifespan
)


def custom_openapi():
    """
        Custom OpenAPI schema with JWT security
    """

    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Posts Service",
        version="1.0.0",
        description="API with JWT authentication",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }

    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(main_router)
app.include_router(mongo_router)
app.include_router(fetcher_router)
app.include_router(auth_router)