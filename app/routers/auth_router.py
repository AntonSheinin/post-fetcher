"""
    Auth endpoints router
"""

import logging
from datetime import datetime, timedelta, timezone

import jwt
from fastapi.security import HTTPAuthorizationCredentials
from fastapi import APIRouter, HTTPException, Query, Depends, Security

from app.auth import SECRET_KEY, ALGORITHM, get_current_user_id, security


logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post("/login")
async def login_for_testing(user_id: int) -> dict:
    """
        Simple login endpoint for testing
    """

    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=1)
    }

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

    return {"access_token": token, "token_type": "bearer"}


@auth_router.get("/me")
async def get_current_user(token: HTTPAuthorizationCredentials = Security(security)) -> dict:
    """
        Get current authenticated user info
    """

    current_user_id = get_current_user_id(token)

    return {"user_id": current_user_id}
