"""
    Date generation utilities for creating random timestamps.
"""

import logging
from random import randint
from datetime import datetime, timedelta, timezone


logger = logging.getLogger(__name__)

def generate_random_date(days_back: int = 365) -> datetime:
    """
        Generate a random datetime within the specified number of days back from now.
    """

    if days_back <= 0:
        raise ValueError("days_back must be positive")

    now = datetime.now(timezone.utc)
    earliest_date = now - timedelta(days=days_back)

    total_seconds = int((now - earliest_date).total_seconds())
    random_seconds = randint(0, total_seconds)

    return earliest_date + timedelta(seconds=random_seconds)


def generate_comment_date(post_created_at: datetime, max_days_after: int = 30) -> datetime:
    """
        Generate a random datetime for a comment after the post creation date.
    """

    if max_days_after <= 0:
        raise ValueError("max_days_after must be positive")

    now = datetime.now(timezone.utc)
    if post_created_at > now:
        raise ValueError("post_created_at cannot be in the future")

    latest_comment_date = min(post_created_at + timedelta(days=max_days_after), now)

    total_seconds = int((latest_comment_date - post_created_at).total_seconds())

    # If range is too small, add 1-60 minutes as fallback
    if total_seconds <= 0:
        random_seconds = randint(60, 3600)
    else:
        random_seconds = randint(0, total_seconds)

    return post_created_at + timedelta(seconds=random_seconds)