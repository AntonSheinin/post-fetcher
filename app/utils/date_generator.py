"""
Date generation utilities for creating random timestamps.
"""
import logging
from datetime import datetime, timedelta, timezone
from random import randint

# Simple logger for this module
logger = logging.getLogger(__name__)


def generate_random_date(days_back: int = 365) -> datetime:
    """Generate a random datetime within the specified number of days back from now."""
    if days_back <= 0:
        raise ValueError("days_back must be positive")

    now = datetime.now(timezone.utc)
    earliest_date = now - timedelta(days=days_back)

    # Generate random number of seconds between earliest_date and now
    total_seconds = int((now - earliest_date).total_seconds())
    random_seconds = randint(0, total_seconds)

    return earliest_date + timedelta(seconds=random_seconds)


def generate_comment_date(post_created_at: datetime, max_days_after: int = 30) -> datetime:
    """Generate a random datetime for a comment after the post creation date."""
    if max_days_after <= 0:
        raise ValueError("max_days_after must be positive")

    now = datetime.now(timezone.utc)
    if post_created_at > now:
        raise ValueError("post_created_at cannot be in the future")

    # Calculate the latest possible comment date
    latest_comment_date = post_created_at + timedelta(days=max_days_after)

    # If latest possible date is in the future, use current time as limit
    if latest_comment_date > now:
        latest_comment_date = now

    # Generate random seconds between post creation and latest comment date
    total_seconds = int((latest_comment_date - post_created_at).total_seconds())

    # Ensure we have at least some time difference (minimum 1 minute after post)
    min_seconds = 60  # 1 minute
    if total_seconds < min_seconds:
        # If the range is too small, just add 1-60 minutes to post time
        random_seconds = randint(60, 3600)  # 1 minute to 1 hour
    else:
        random_seconds = randint(min_seconds, total_seconds)

    return post_created_at + timedelta(seconds=random_seconds)