"""
    Main endpoints router
"""

import logging
from typing import List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Query, Depends

from app.services.post_service import PostService
from app.models.schemas import (
    PostResponse,
    CommentResponse,
    CommentSearchResponse,
    PostCountResponse,
    PostUpdateRequest
)


logger = logging.getLogger(__name__)

main_router = APIRouter(prefix="/posts", tags=["posts"])

def get_post_service() -> PostService:
    """
        Dependency to get PostService instance.
    """

    return PostService()


@main_router.get("/{post_id}", response_model=PostResponse)
async def get_post(
    post_id: int,
    post_service: PostService = Depends(get_post_service)
) -> PostResponse:
    """
        Get post by id without comments.
    """

    result = await post_service.get_post_response_only(post_id)

    if not result:
        raise HTTPException(status_code=404, detail="Post not found")

    return result


@main_router.get("/{post_id}/comments", response_model=List[CommentResponse])
async def get_post_comments(
    post_id: int,
    post_service: PostService = Depends(get_post_service)
) -> list:
    """
        Get comments for a specific post.
    """

    comments = await post_service.get_comments_only(post_id)

    if comments is None:
        raise HTTPException(status_code=404, detail="Post not found")

    return comments


@main_router.get("/comments/search", response_model=CommentSearchResponse)
async def search_comments(
    query: str = Query(..., min_length=1),
    limit: int = Query(default=100, ge=1, le=1000),
    post_service: PostService = Depends(get_post_service)
) -> CommentSearchResponse:
    """
        Get comments by free search text.
    """

    return await post_service.search_comments(query, limit)


@main_router.get("/count", response_model=PostCountResponse)
async def get_posts_count(
    start_date: datetime = Query(default=None),
    end_date: datetime = Query(default=None),
    post_service: PostService = Depends(get_post_service)
) -> PostCountResponse:
    """
        Get total count of posts in a given date range.
    """

    return await post_service.count_posts_in_date_range(start_date, end_date)


@main_router.put("/{post_id}")
async def update_post(
    post_id: int,
    update_data: PostUpdateRequest,
    post_service: PostService = Depends(get_post_service)
) -> dict:
    """
        Edit post message.
    """

    success = await post_service.update_post_body(post_id, update_data)

    if not success:
        raise HTTPException(status_code=404, detail="Post not found")

    return {"message": "Post updated successfully"}


@main_router.get("/comments/{comment_id}", response_model=CommentResponse)
async def get_comment(
    comment_id: int,
    post_service: PostService = Depends(get_post_service)
) -> CommentResponse:
    """
        Get comment by id.
    """

    result = await post_service.get_comment_by_id(comment_id)

    if not result:
        raise HTTPException(status_code=404, detail="Comment not found")

    return result