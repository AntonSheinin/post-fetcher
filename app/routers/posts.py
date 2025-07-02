"""
API endpoints for posts and comments.
"""
import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

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

# Simple logger for this module
logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("/{post_id}/comments", response_model=PostCommentsResponse)
async def get_post_comments(post_id: int):
    """Get post comments by post id."""
    logger.info(f"Getting comments for post {post_id}")

    result = await get_post_with_comments(post_id)
    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    return result


@router.get("/comments/search", response_model=CommentSearchResponse)
async def search_comments(
        q: str = Query(..., min_length=1, description="Search query"),
        limit: int = Query(default=100, ge=1, le=1000, description="Maximum results")
):
    """Get comments by free search text."""
    logger.info(f"Searching comments for: '{q}'")

    return await search_comments_by_text(q, limit)


@router.get("/count", response_model=PostCountResponse)
async def get_posts_count(
        start_date: Optional[datetime] = Query(default=None, description="Start date (ISO format)"),
        end_date: Optional[datetime] = Query(default=None, description="End date (ISO format)")
):
    """Get total count of posts in a given date range."""
    logger.info(f"Counting posts from {start_date} to {end_date}")

    return await count_posts_by_date_range(start_date, end_date)


@router.put("/{post_id}", response_model=dict)
async def update_post(post_id: int, update_data: PostUpdateRequest):
    """Edit post message."""
    logger.info(f"Updating post {post_id}")

    success = await update_post_content(post_id, update_data.body)
    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"message": "Post updated successfully"}