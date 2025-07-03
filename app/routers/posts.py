"""
API routers for posts, mongo operations, and fetcher control.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query

from app.services.post_service import (
    get_post_with_comments,
    search_comments_by_text,
    count_posts_by_date_range,
    update_post_content
)
from app.models.schemas import (
    PostCommentsResponse,
    CommentSearchResponse,
    PostCountResponse,
    PostUpdateRequest
)
from app.models.database import get_posts_collection

# Simple logger for this module
logger = logging.getLogger(__name__)

# ============================================================================
# MAIN ROUTER - Production endpoints
# ============================================================================
main_router = APIRouter(prefix="/posts", tags=["posts"])


@main_router.get("/{post_id}/comments", response_model=PostCommentsResponse)
async def get_post_comments(post_id: int):
    """Get post comments by post id."""
    result = await get_post_with_comments(post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")
    return result


@main_router.get("/comments/search", response_model=CommentSearchResponse)
async def search_comments(
    q: str = Query(..., min_length=1),
    limit: int = Query(default=100, ge=1, le=1000)
):
    """Get comments by free search text."""
    return await search_comments_by_text(q, limit)


@main_router.get("/count", response_model=PostCountResponse)
async def get_posts_count(
    start_date: Optional[datetime] = Query(default=None),
    end_date: Optional[datetime] = Query(default=None)
):
    """Get total count of posts in a given date range."""
    return await count_posts_by_date_range(start_date, end_date)


@main_router.put("/{post_id}")
async def update_post(post_id: int, update_data: PostUpdateRequest):
    """Edit post message."""
    success = await update_post_content(post_id, update_data.body)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")
    return {"message": "Post updated successfully"}


# ============================================================================
# MONGO ROUTER - Database operations
# ============================================================================
mongo_router = APIRouter(prefix="/mongo", tags=["mongo"])


@mongo_router.get("/clear")
async def clear_all_data():
    """Delete all fetched data from MongoDB."""
    posts_collection = await get_posts_collection()
    result = await posts_collection.delete_many({})
    return {
        "message": "All data cleared successfully",
        "deleted_count": result.deleted_count
    }


@mongo_router.get("/all")
async def get_all_records():
    """Get all fetched records from MongoDB."""
    posts_collection = await get_posts_collection()

    cursor = posts_collection.find({})
    posts = await cursor.to_list(length=None)

    # Convert ObjectId to string for JSON serialization
    for post in posts:
        if "_id" in post:
            post["_id"] = str(post["_id"])

    return {
        "total_posts": len(posts),
        "posts": posts
    }


# ============================================================================
# FETCHER ROUTER - Background task control
# ============================================================================
fetcher_router = APIRouter(prefix="/fetcher", tags=["fetcher"])


@fetcher_router.get("/start")
async def start_fetcher():
    """Start the background fetcher task."""
    from app.services.background_tasks import start_fetcher as start_bg_fetcher

    success = start_bg_fetcher()
    if success:
        return {"message": "Fetcher started successfully"}
    else:
        return {"message": "Fetcher is already running"}


@fetcher_router.get("/stop")
async def stop_fetcher():
    """Stop the background fetcher task."""
    from app.services.background_tasks import stop_fetcher as stop_bg_fetcher

    success = stop_bg_fetcher()
    if success:
        return {"message": "Fetcher stopped successfully"}
    else:
        return {"message": "Fetcher is not running"}


@fetcher_router.get("/status")
async def get_fetcher_status():
    """Get current fetcher status."""
    from app.services.background_tasks import get_fetcher_status as get_bg_status

    return get_bg_status()


# Export all routers for easy import
__all__ = ["main_router", "mongo_router", "fetcher_router"]