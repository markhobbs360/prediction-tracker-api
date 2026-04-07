import logging
from datetime import datetime, timedelta, timezone
from uuid import UUID

import jwt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)


def verify_google_token(token: str, client_id: str) -> dict | None:
    """Verify a Google OAuth2 ID token and return the payload.

    Returns None if verification fails.
    """
    try:
        payload = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            client_id,
        )
        return payload
    except Exception:
        logger.exception("Google token verification failed")
        return None


def create_jwt(user_id: UUID, secret: str, expiry_hours: int = 24) -> str:
    """Create a signed JWT for the given user."""
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "iat": now,
        "exp": now + timedelta(hours=expiry_hours),
    }
    return jwt.encode(payload, secret, algorithm="HS256")


def decode_jwt(token: str, secret: str) -> dict | None:
    """Decode and validate a JWT. Returns the payload or None if invalid."""
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        logger.warning("JWT has expired")
        return None
    except jwt.InvalidTokenError:
        logger.warning("Invalid JWT")
        return None
