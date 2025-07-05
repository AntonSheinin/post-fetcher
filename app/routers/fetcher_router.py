"""
    Fetcher endpoints router
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.services.background_tasks import start_fetcher, stop_fetcher, get_fetcher_status


logger = logging.getLogger(__name__)

fetcher_router = APIRouter(prefix="/fetcher", tags=["fetcher"])

@fetcher_router.get("/start")
async def start_fetcher_endpoint() -> dict:
    """
        Start the background fetcher task.
    """

    success = start_fetcher()

    if success:
        return {"message": "Fetcher started successfully"}

    else:
        return {"message": "Fetcher is already running"}

@fetcher_router.get("/stop")
async def stop_fetcher_endpoint() -> dict:
    """
        Stop the background fetcher task.
    """

    success = stop_fetcher()

    if success:
        return {"message": "Fetcher stopped successfully"}

    else:
        return {"message": "Fetcher is not running"}


@fetcher_router.get("/status")
async def get_fetcher_status_endpoint() -> dict:
    """
        Get current fetcher status.
    """

    return get_fetcher_status()
