"""
Post service for managing post and comment operations.
"""
import logging
from datetime import datetime, timezone
from typing import Optional

from app.models.schemas import (
    PostModel, PostResponse, CommentResponse,
    PostCommentsResponse, CommentSearchResponse, PostCountResponse,
    PostUpdateRequest
)
from app.models.database import get_posts_collection

# Simple logger for this module
logger = logging.getLogger(__name__)


class PostService:
    """Service class for post and comment operations."""

    async def get_post_by_id(self, post_id: int) -> Optional[PostModel]:
        """Retrieve a post by its ID."""
        posts_collection = await get_posts_collection()

        post_doc = await posts_collection.find_one({"post_id": post_id})

        if post_doc:
            # Convert ObjectId to string for Pydantic
            if "_id" in post_doc:
                post_doc["_id"] = str(post_doc["_id"])
            return PostModel(**post_doc)
        return None

    async def get_post_comments(self, post_id: int) -> Optional[PostCommentsResponse]:
        """Get a post with all its comments."""
        post_model = await self.get_post_by_id(post_id)

        if not post_model:
            return None

        # Transform to response models
        post_response = PostResponse(
            post_id=post_model.post_id,
            user_id=post_model.user_id,
            title=post_model.title,
            body=post_model.body,
            created_at=post_model.created_at,
            comment_count=len(post_model.comments)
        )

        comment_responses = [
            CommentResponse(
                comment_id=comment.comment_id,
                post_id=comment.post_id,
                name=comment.name,
                email=comment.email,
                body=comment.body,
                created_at=comment.created_at
            )
            for comment in post_model.comments
        ]

        return PostCommentsResponse(
            post=post_response,
            comments=comment_responses
        )

    async def search_comments(self, query: str, limit: int = 100) -> CommentSearchResponse:
        """Search for comments containing the specified text."""
        if not query.strip():
            raise ValueError("Search query cannot be empty")

        posts_collection = await get_posts_collection()

        # Use regex for simple text search
        regex_filter = {
            "comments.body": {"$regex": query, "$options": "i"}
        }

        cursor = posts_collection.find(regex_filter).limit(limit)
        matching_posts = await cursor.to_list(length=None)

        # Extract all matching comments
        all_comments = []
        for post_doc in matching_posts:
            for comment_data in post_doc.get("comments", []):
                # Check if this comment matches the query
                if query.lower() in comment_data.get("body", "").lower():
                    comment_response = CommentResponse(
                        comment_id=comment_data["comment_id"],
                        post_id=comment_data["post_id"],
                        name=comment_data["name"],
                        email=comment_data["email"],
                        body=comment_data["body"],
                        created_at=comment_data["created_at"]
                    )
                    all_comments.append(comment_response)

        # Limit results
        limited_comments = all_comments[:limit]

        return CommentSearchResponse(
            comments=limited_comments,
            total_count=len(all_comments),
            query=query
        )

    async def count_posts_in_date_range(self, start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> PostCountResponse:
        """Count posts created within a specified date range."""
        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        posts_collection = await get_posts_collection()

        # Build date filter
        date_filter = {}
        if start_date or end_date:
            date_filter["created_at"] = {}
            if start_date:
                date_filter["created_at"]["$gte"] = start_date
            if end_date:
                date_filter["created_at"]["$lte"] = end_date

        # Count documents matching the filter
        count = await posts_collection.count_documents(date_filter)

        return PostCountResponse(
            count=count,
            start_date=start_date,
            end_date=end_date
        )

    async def update_post_body(self, post_id: int, update_request: PostUpdateRequest) -> bool:
        """Update the body content of a post."""
        posts_collection = await get_posts_collection()

        # Update the post body
        update_filter = {"post_id": post_id}
        update_operation = {
            "$set": {
                "body": update_request.body,
                "updated_at": datetime.now(timezone.utc)
            }
        }

        result = await posts_collection.update_one(update_filter, update_operation)

        return result.modified_count == 1


# Global service instance
post_service = PostService()


# Convenience functions for use in FastAPI routes
async def get_post_with_comments(post_id: int) -> Optional[PostCommentsResponse]:
    """Get a post with its comments."""
    return await post_service.get_post_comments(post_id)


async def search_comments_by_text(query: str, limit: int = 100) -> CommentSearchResponse:
    """Search comments by text."""
    return await post_service.search_comments(query, limit)


async def count_posts_by_date_range(start_date: Optional[datetime] = None,
                                   end_date: Optional[datetime] = None) -> PostCountResponse:
    """Count posts in a date range."""
    return await post_service.count_posts_in_date_range(start_date, end_date)


async def update_post_content(post_id: int, new_body: str) -> bool:
    """Update post content."""
    update_request = PostUpdateRequest(body=new_body)
    return await post_service.update_post_body(post_id, update_request)