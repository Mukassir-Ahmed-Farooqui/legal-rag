"""
JWT creation and verification utilities.
"""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from dotenv import load_dotenv
import os

load_dotenv()

JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_MINUTES: int = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))


def create_access_token(
    user_id: str,
    email: str,
    expires_delta: timedelta | None = None,
) -> str:
    """
    Create a signed JWT access token.

    Payload:
        sub   — user id (string UUID)
        email — user email
        exp   — expiration timestamp
    """
    now = datetime.now(timezone.utc)
    expire = now + (expires_delta or timedelta(minutes=JWT_EXPIRE_MINUTES))

    payload: dict[str, Any] = {
        "sub": user_id,
        "email": email,
        "exp": expire,
    }

    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)


def verify_access_token(token: str) -> dict[str, Any]:
    """
    Decode and verify a JWT access token.

    Returns the payload dict on success.
    Raises JWTError on invalid/expired tokens.
    """
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
    except JWTError:
        raise

    if "sub" not in payload or "email" not in payload:
        raise JWTError("Token payload missing required claims (sub, email)")

    return payload
