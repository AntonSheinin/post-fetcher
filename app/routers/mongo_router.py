"""
    Mongo endpoints router
"""

import logging

from fastapi import APIRouter, HTTPException, Query

from app.models.database import get_posts_collection


logger = logging.getLogger(__name__)

mongo_router = APIRouter(prefix="/mongo", tags=["mongo"])

@mongo_router.get("/clear")
async def clear_all_data() -> dict:
    """
        Delete all fetched data from MongoDB.
    """

    posts_collection = await get_posts_collection()
    result = await posts_collection.delete_many({})

    return {
        "message": "All data cleared successfully",
        "deleted_count": result.deleted_count
    }


@mongo_router.get("/all")
async def get_all_records() -> dict:
    """
        Get all fetched records from MongoDB.
    """

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

