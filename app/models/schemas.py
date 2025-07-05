"""
    Pydantic models for API requests, responses, and data validation.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional

from pydantic import BaseModel, Field, ConfigDict, field_validator, computed_field


logger = logging.getLogger(__name__)

class CommentModel(BaseModel):
    """
        Model for comment data.
    """

    comment_id: int = Field(..., gt=0)
    post_id: int = Field(..., gt=0)
    name: str = Field(..., min_length=1, max_length=500)
    email: str = Field(...)
    body: str = Field(..., min_length=1, max_length=2000)
    created_at: datetime

    @field_validator('body')
    @classmethod
    def validate_body(cls, v: str) -> str:
        """
            Validate body content.
        """

        if not v.strip():
            raise ValueError("Body cannot be empty")

        return v.strip()


class PostModel(BaseModel):
    """
        Model for post data storage in MongoDB.
    """

    id: Optional[str] = Field(default=None, alias="_id")
    post_id: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
    title: str = Field(..., min_length=1, max_length=500)
    body: str = Field(..., min_length=1, max_length=5000)
    created_at: datetime
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: Optional[datetime] = Field(default=None)
    comments: List[CommentModel] = Field(default_factory=list)

    model_config = ConfigDict(populate_by_name=True)

    @computed_field
    @property
    def comment_count(self) -> int:
        """
            Number of comments.
        """

        return len(self.comments)

    @field_validator('title', 'body')
    @classmethod
    def validate_text(cls, v: str) -> str:
        """
            Validate text content.
        """

        if not v.strip():
            raise ValueError("Text cannot be empty")

        return v.strip()


class PostUpdateRequest(BaseModel):
    """
        Request model for updating post content.
    """

    body: str = Field(..., min_length=1, max_length=5000)

    @field_validator('body')
    @classmethod
    def validate_body(cls, v: str) -> str:
        """
            Validate body content.
        """

        if not v.strip():
            raise ValueError("Body cannot be empty")

        return v.strip()


class PostResponse(BaseModel):
    """
        Response model for post data.
    """

    post_id: int
    user_id: int
    title: str
    body: str
    created_at: datetime
    comment_count: int = Field(..., ge=0)


class CommentResponse(BaseModel):
    """
        Response model for comment data.
    """

    comment_id: int
    post_id: int
    name: str
    email: str
    body: str
    created_at: datetime


class CommentSearchResponse(BaseModel):
    """
        Response model for comment search results.
    """

    comments: List[CommentResponse]
    total_count: int = Field(..., ge=0)
    query: str


class PostCountResponse(BaseModel):
    """
        Response model for post count queries.
    """

    count: int = Field(..., ge=0)
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None