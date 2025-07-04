"""
    Main endpoints router
"""

import logging
from typing import List
from datetime import datetime

import jwt
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter, HTTPException, Query, Depends, Security

from app.auth import security
from app.services.post_service import PostService
from app.routers.auth_router import get_current_user_id
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
        token: HTTPAuthorizationCredentials = Security(security),
        post_service: PostService = Depends(get_post_service)
) -> dict:
    """
        Edit post message (only by author)
    """

    logger.info(f"Post updating request, post ID: {post_id}, update_data: {update_data}")

    post = await post_service.get_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    current_user_id = get_current_user_id(token)

    if post.user_id != current_user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this post")

    success = await post_service.update_post_body(post_id, update_data)
    return {"message": "Post updated successfully"} if success else {"message": "Post updated failed"}


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

