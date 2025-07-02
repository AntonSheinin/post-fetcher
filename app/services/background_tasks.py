"""
Background task for periodic data fetching.
"""
import asyncio
import os
import logging

from app.services.fetcher import fetch_and_store_posts

# Simple logger for this module
logger = logging.getLogger(__name__)


async def periodic_fetcher():
    """Run periodic data fetching in background."""
    interval = int(os.getenv("FETCH_INTERVAL_SECONDS", "60"))

    while True:
        try:
            await fetch_and_store_posts()
        except Exception as e:
            logger.error(f"Fetch failed: {e}")

        await asyncio.sleep(interval)