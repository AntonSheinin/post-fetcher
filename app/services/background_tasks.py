"""
Background task for periodic data fetching.
"""
import asyncio
import os
import logging

from app.services.fetcher import fetch_and_store_posts

# Simple logger for this module
logger = logging.getLogger(__name__)

# Global fetcher task and control
fetcher_task = None
fetcher_running = False


async def periodic_fetcher():
    """Run periodic data fetching in background."""
    global fetcher_running
    interval = int(os.getenv("FETCH_INTERVAL_SECONDS", "60"))
    fetcher_running = True

    while fetcher_running:
        try:
            await fetch_and_store_posts()
        except Exception as e:
            logger.error(f"Fetch failed: {e}")

        # Check if still running before sleeping
        if fetcher_running:
            await asyncio.sleep(interval)


def start_fetcher():
    """Start the background fetcher task."""
    global fetcher_task, fetcher_running

    if fetcher_task is None or fetcher_task.done():
        logger.info("Starting background fetcher")
        fetcher_task = asyncio.create_task(periodic_fetcher())
        return True
    else:
        logger.warning("Fetcher is already running")
        return False


def stop_fetcher():
    """Stop the background fetcher task."""
    global fetcher_task, fetcher_running

    if fetcher_task and not fetcher_task.done():
        logger.info("Stopping background fetcher")
        fetcher_running = False
        fetcher_task.cancel()
        fetcher_task = None
        return True
    else:
        logger.warning("Fetcher is not running")
        return False


def get_fetcher_status():
    """Get current fetcher status."""
    global fetcher_task, fetcher_running

    if fetcher_task is None:
        return {"status": "stopped", "running": False}
    elif fetcher_task.done():
        return {"status": "stopped", "running": False}
    elif fetcher_running:
        return {"status": "running", "running": True}
    else:
        return {"status": "stopping", "running": False}