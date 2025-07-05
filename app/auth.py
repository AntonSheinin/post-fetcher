"""
    Authentication utilities and dependencies.
"""
import os
import logging
import traceback

import jwt
from fastapi import HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordBearer


SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secret-key-not-found-in-env")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

security = HTTPBearer(scheme_name="BearerAuth")

logger = logging.getLogger(__name__)

def get_current_user_id(token: HTTPAuthorizationCredentials) -> int:
    """
        Extract and validate user ID from JWT token
    """

    try:
        payload = jwt.decode(
            token.credentials,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        user_id: int = payload.get("user_id")

        if user_id is None:
            logger.error("User ID was not found in JWT")
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user_id"
            )

        logger.info(f"User ID: {user_id}")
        return user_id

    except jwt.ExpiredSignatureError:
        logger.error("Token was expired")
        raise HTTPException(status_code=401, detail="Token expired")

    except jwt.InvalidTokenError:
        logger.error("Invalid token")
        raise HTTPException(status_code=401, detail="Invalid token")

    except Exception as e:
        logger.error(f"Token validation failed, error: {str(e)}")
        raise HTTPException(status_code=401, detail="Token validation failed")