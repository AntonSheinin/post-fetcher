"""
    Background task for periodic data fetching.
"""

import os
import asyncio
import logging

from app.services.fetcher_service import fetch_and_store_posts


logger = logging.getLogger(__name__)

# Global state
_fetcher_task = None
_fetcher_running = False


async def _periodic_fetcher() -> None:
    """
        Run periodic data fetching in background.
    """

    global _fetcher_running

    interval = int(os.getenv("FETCH_INTERVAL_SECONDS", "60"))
    _fetcher_running = True

    while _fetcher_running:
        try:
            await fetch_and_store_posts()

        except Exception as e:
            logger.error(f"Fetch failed: {e}")

        # Only sleep if still running
        if _fetcher_running:
            await asyncio.sleep(interval)


def start_fetcher() -> bool:
    """
        Start the background fetcher task.
    """

    global _fetcher_task, _fetcher_running

    if _fetcher_task is None or _fetcher_task.done():
        logger.info("Starting background fetcher")
        _fetcher_task = asyncio.create_task(_periodic_fetcher())
        return True

    else:
        logger.warning("Fetcher is already running")
        return False


def stop_fetcher() -> bool:
    """
        Stop the background fetcher task.
    """

    global _fetcher_task, _fetcher_running

    if _fetcher_task and not _fetcher_task.done():
        logger.info("Stopping background fetcher")
        _fetcher_running = False
        _fetcher_task.cancel()
        _fetcher_task = None
        return True

    else:
        logger.warning("Fetcher is not running")
        return False


def get_fetcher_status() -> dict:
    """
        Get current fetcher status.
    """

    global _fetcher_task, _fetcher_running

    if _fetcher_task is None:
        return {"status": "stopped", "running": False}

    elif _fetcher_task.done():
        return {"status": "stopped", "running": False}

    elif _fetcher_running:
        return {"status": "running", "running": True}

    else:
        return {"status": "stopping", "running": False}