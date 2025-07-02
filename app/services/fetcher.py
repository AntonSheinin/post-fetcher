"""
Data fetcher service for retrieving posts and comments from external API.
"""
import os
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Set

import httpx
from dotenv import load_dotenv

from app.models.schemas import PostModel, CommentModel
from app.models.database import get_posts_collection
from app.utils.date_generator import generate_random_date, generate_comment_date

# Load environment variables
load_dotenv()

# Simple logger for this module
logger = logging.getLogger(__name__)


class FetcherService:
    """Service for fetching posts and comments from external API."""

    def __init__(self) -> None:
        """Initialize the FetcherService."""
        self.base_url: str = os.getenv("JSONPLACEHOLDER_BASE_URL", "https://jsonplaceholder.typicode.com")
        self.max_posts_per_fetch: int = int(os.getenv("MAX_POSTS_PER_FETCH", "10"))
        self.date_range_days: int = int(os.getenv("RANDOM_DATE_RANGE_DAYS", "365"))
        self._client: httpx.AsyncClient = httpx.AsyncClient(timeout=30.0)

    async def close(self) -> None:
        """Close HTTP client."""
        await self._client.aclose()

    async def fetch_posts(self) -> List[Dict[str, Any]]:
        """Fetch posts from external API."""
        logger.info("Fetching posts from external API")

        response = await self._client.get(f"{self.base_url}/posts")
        response.raise_for_status()

        posts_data = response.json()
        logger.info(f"Fetched {len(posts_data)} posts from API")

        return posts_data

    async def fetch_comments_for_post(self, post_id: int) -> List[Dict[str, Any]]:
        """Fetch comments for a specific post."""
        response = await self._client.get(f"{self.base_url}/posts/{post_id}/comments")
        response.raise_for_status()

        return response.json()

    async def get_existing_post_ids(self) -> Set[int]:
        """Get set of existing post IDs from database."""
        posts_collection = await get_posts_collection()

        cursor = posts_collection.find({}, {"post_id": 1, "_id": 0})
        existing_posts = await cursor.to_list(length=None)

        return {post["post_id"] for post in existing_posts}

    def transform_post_data(self, post_data: Dict[str, Any], comments_data: List[Dict[str, Any]]) -> PostModel:
        """Transform raw API data into PostModel."""
        # Generate random creation date for post
        post_created_at = generate_random_date(self.date_range_days)

        # Transform comments with dates after post creation
        transformed_comments = []
        for comment_data in comments_data:
            comment_created_at = generate_comment_date(post_created_at)

            comment = CommentModel(
                comment_id=comment_data["id"],
                post_id=comment_data["postId"],
                name=comment_data["name"],
                email=comment_data["email"],
                body=comment_data["body"],
                created_at=comment_created_at
            )
            transformed_comments.append(comment)

        # Create post model
        return PostModel(
            post_id=post_data["id"],
            user_id=post_data["userId"],
            title=post_data["title"],
            body=post_data["body"],
            created_at=post_created_at,
            comments=transformed_comments
        )

    async def save_post(self, post_model: PostModel) -> None:
        """Save post to database."""
        posts_collection = await get_posts_collection()

        # Convert to dict for MongoDB insertion
        post_dict = post_model.model_dump(by_alias=True, exclude={"id"})

        await posts_collection.insert_one(post_dict)

    async def fetch_and_store_data(self) -> Dict[str, Any]:
        """Main method to fetch posts and comments, then store new ones."""
        logger.info("Starting fetch and store operation")
        start_time = datetime.now(timezone.utc)

        # Fetch all posts from API
        all_posts = await self.fetch_posts()

        # Get existing post IDs to avoid duplicates
        existing_ids = await self.get_existing_post_ids()

        # Filter new posts and limit to max per fetch
        new_posts = [post for post in all_posts if post["id"] not in existing_ids]
        posts_to_process = new_posts[:self.max_posts_per_fetch]

        logger.info(f"Processing {len(posts_to_process)} new posts")

        # Process each new post
        stored_count = 0
        for post_data in posts_to_process:
            try:
                # Fetch comments for this post
                comments_data = await self.fetch_comments_for_post(post_data["id"])

                # Transform and validate data
                post_model = self.transform_post_data(post_data, comments_data)

                # Save to database
                await self.save_post(post_model)
                stored_count += 1

            except Exception as e:
                logger.error(f"Failed to process post {post_data.get('id')}: {e}")
                continue

        processing_time = (datetime.now(timezone.utc) - start_time).total_seconds()

        result = {
            "total_fetched": len(all_posts),
            "new_posts": stored_count,
            "skipped_posts": len(all_posts) - len(new_posts),
            "processing_time": processing_time
        }

        logger.info(f"Fetch operation completed: {result}")
        return result


# Global fetcher service functions
async def fetch_and_store_posts() -> Dict[str, Any]:
    """Convenience function to fetch and store posts."""
    logger.info("Starting fetch and store posts operation")

    fetcher = FetcherService()
    try:
        return await fetcher.fetch_and_store_data()
    finally:
        await fetcher.close()