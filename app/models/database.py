"""
    MongoDB database connection management using PyMongo Async API.
"""

import os
import logging
from typing import Optional

from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.collection import AsyncCollection
from pymongo.asynchronous.mongo_client import AsyncMongoClient


logger = logging.getLogger(__name__)

class DatabaseManager:
    """
        manages MongoDB async connection and operations.
    """

    def __init__(self) -> None:
        """
            Initialize the DatabaseManager.
        """

        self._client: Optional[AsyncMongoClient] = None
        self._database: Optional[AsyncDatabase] = None
        self._is_connected: bool = False

    async def connect(self) -> None:
        """
            Establish connection to MongoDB.
        """

        logger.info("Connecting to MongoDB")

        self._client = AsyncMongoClient(
            os.getenv("MONGODB_URL"),
            serverSelectionTimeoutMS=5000,
            connectTimeoutMS=5000
        )

        # Test connection
        await self._client.admin.command('ping')

        self._database = self._client[os.getenv("DATABASE_NAME")]
        self._is_connected = True

        await self._create_indexes()

        logger.info("Successfully connected to MongoDB")

    async def disconnect(self) -> None:
        """
            Close database connection.
        """

        if self._client:
            self._client.close()
            self._is_connected = False
            logger.info("Disconnected from MongoDB")

        self._client = None
        self._database = None

    async def _create_indexes(self) -> None:
        """
            Create required database indexes.
        """

        posts_collection = self.get_posts_collection()

        await posts_collection.create_index("post_id", unique=True)
        await posts_collection.create_index("created_at")
        await posts_collection.create_index("comments.body")

        logger.info("Database indexes created")

    def get_database(self) -> AsyncDatabase:
        """
            Get database instance.
        """

        if not self._is_connected or self._database is None:
            logger.error("Database not connected")
            raise ConnectionError("Database not connected")

        return self._database

    def get_posts_collection(self) -> AsyncCollection:
        """
            Get posts collection.
        """

        return self.get_database()["posts"]

database_manager = DatabaseManager()

async def get_posts_collection() -> AsyncCollection:
    """
        Dependency function to get posts collection.
    """

    return database_manager.get_posts_collection()