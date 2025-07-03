"""
    Post service for managing post and comment operations.
"""

import logging
from typing import List
from datetime import datetime, timezone

from app.models.schemas import (
    PostModel,
    PostResponse,
    CommentResponse,
    CommentSearchResponse,
    PostCountResponse,
    PostUpdateRequest
)
from app.models.database import get_posts_collection


logger = logging.getLogger(__name__)

class PostService:
    """
        Service class for post and comment operations.
    """

    @staticmethod
    async def get_post_by_id(post_id: int) -> PostModel | None:
        """
            Retrieve a post by its ID.
        """
        posts_collection = await get_posts_collection()
        post_doc = await posts_collection.find_one({"post_id": post_id})

        if post_doc:
            # Convert ObjectId to string for Pydantic
            if "_id" in post_doc:
                post_doc["_id"] = str(post_doc["_id"])
            return PostModel(**post_doc)

        return None

    async def get_post_response_only(self, post_id: int) -> PostResponse | None:
        """
            Get only post data without comments.
        """

        post_model = await self.get_post_by_id(post_id)

        if not post_model:
            return None

        return PostResponse(
            post_id=post_model.post_id,
            user_id=post_model.user_id,
            title=post_model.title,
            body=post_model.body,
            created_at=post_model.created_at,
            comment_count=len(post_model.comments)
        )

    async def get_comments_only(self, post_id: int) -> List[CommentResponse] | None:
        """
            Get only comments for a specific post.
        """

        post_model = await self.get_post_by_id(post_id)

        if not post_model:
            return None

        return [
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

    @staticmethod
    async def get_comment_by_id(comment_id: int) -> CommentResponse | None:
        """
            Get a specific comment by its ID.
        """

        posts_collection = await get_posts_collection()

        # Find post containing the comment
        post_doc = await posts_collection.find_one(
            {"comments.comment_id": comment_id},
            {"comments.$": 1}
        )

        if not post_doc or "comments" not in post_doc:
            return None

        # Extract the specific comment
        comment_data = post_doc["comments"][0]

        return CommentResponse(
            comment_id=comment_data["comment_id"],
            post_id=comment_data["post_id"],
            name=comment_data["name"],
            email=comment_data["email"],
            body=comment_data["body"],
            created_at=comment_data["created_at"]
        )

    @staticmethod
    async def search_comments(query: str, limit: int = 100) -> CommentSearchResponse:
        """
            Search for comments containing the specified text.
        """

        if not query.strip():
            raise ValueError("Search query cannot be empty")

        posts_collection = await get_posts_collection()

        regex_filter = {
            "comments.body": {"$regex": query, "$options": "i"}
        }

        cursor = posts_collection.find(regex_filter).limit(limit)
        matching_posts = await cursor.to_list(length=None)

        all_comments = []
        for post_doc in matching_posts:
            for comment_data in post_doc.get("comments", []):
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

        limited_comments = all_comments[:limit]

        return CommentSearchResponse(
            comments=limited_comments,
            total_count=len(all_comments),
            query=query
        )

    @staticmethod
    async def count_posts_in_date_range(start_date: datetime = None, end_date: datetime = None) -> PostCountResponse:
        """
            Count posts created within a specified date range.
        """

        if start_date and end_date and start_date > end_date:
            raise ValueError("start_date cannot be after end_date")

        posts_collection = await get_posts_collection()

        date_filter = {}

        if start_date or end_date:
            date_filter["created_at"] = {}

            if start_date:
                date_filter["created_at"]["$gte"] = start_date

            if end_date:
                date_filter["created_at"]["$lte"] = end_date

        count = await posts_collection.count_documents(date_filter)

        return PostCountResponse(
            count=count,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    async def update_post_body(post_id: int, update_request: PostUpdateRequest) -> bool:
        """
            Update the body content of a post.
        """

        posts_collection = await get_posts_collection()

        update_filter = {"post_id": post_id}
        update_operation = {
            "$set": {
                "body": update_request.body,
                "updated_at": datetime.now(timezone.utc)
            }
        }

        result = await posts_collection.update_one(update_filter, update_operation)

        return result.modified_count == 1