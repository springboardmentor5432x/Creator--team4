"""
security.py - JWT Security Utilities

Handles all JWT (JSON Web Token) operations for the authentication system:
  - Token creation with role and user_id claims
  - Token decoding with signature/expiry verification
  - Token verification with proper HTTP error responses

Why a separate security.py?
  auth.py  → password hashing (bcrypt/Passlib) — synchronous, no HTTP context
  security.py → JWT operations (python-jose) — may raise HTTPExceptions directly

Token lifecycle:
  Login → create_access_token() → JWT string sent to client
  Request → verify_token() → decoded payload → get_current_user() → UserInDB
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import HTTPException, status
from jose import ExpiredSignatureError, JWTError, jwt

from config import settings


# ---------------------------------------------------------------------------
# Token Creation
# ---------------------------------------------------------------------------

def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Generate a signed JWT access token.

    The standard payload shape for this application is:
        {
            "sub":     "user@example.com",  # RFC 7519 subject claim (email)
            "user_id": 1,                    # integer PK — avoids an extra DB lookup
            "role":    "Creator",            # RBAC role string
            "exp":     <unix timestamp>,     # set automatically below
        }

    Args:
        data:          Dict to encode into the token. Should contain "sub",
                       "user_id", and "role" at minimum.
        expires_delta: Override the default expiry window. If omitted, uses
                       ACCESS_TOKEN_EXPIRE_MINUTES from config.

    Returns:
        A compact, URL-safe signed JWT string (header.payload.signature).

    Security note:
        The token is signed with SECRET_KEY using ALGORITHM (HS256).
        Any tampering with the payload will cause signature verification
        to fail when the token is later decoded.
    """
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    # "exp" is a standard JWT registered claim (RFC 7519 §4.1.4)
    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
    return encoded_jwt


# ---------------------------------------------------------------------------
# Token Decoding (soft — returns None on failure)
# ---------------------------------------------------------------------------

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decode and validate a JWT access token without raising HTTP exceptions.

    This is a lower-level helper. Callers must handle the `None` return case
    themselves (typically by raising HTTPException 401).

    Prefer `verify_token()` in FastAPI route dependencies, which raises the
    correct HTTP 401 automatically.

    Args:
        token: The raw JWT string extracted from the Authorization header.

    Returns:
        The decoded payload dict if the token is valid and not expired.
        None if the token is invalid, expired, or has a bad signature.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError:
        # Covers: ExpiredSignatureError, JWTClaimsError, DecodeError, etc.
        return None


# ---------------------------------------------------------------------------
# Token Verification (hard — raises HTTPException on failure)
# ---------------------------------------------------------------------------

def verify_token(token: str) -> dict:
    """
    Decode and validate a JWT, raising appropriate HTTP exceptions on failure.

    This is the preferred function to use inside FastAPI dependencies because
    it converts every jwt error into a proper HTTP response automatically.

    Error mapping:
        ExpiredSignatureError  → 401 "Token has expired"
        JWTError (other)       → 401 "Invalid token"
        Missing "sub" claim    → 401 "Token missing subject claim"

    Args:
        token: The raw JWT string from the Authorization: Bearer header.

    Returns:
        The decoded payload dict on success.

    Raises:
        HTTPException 401: For any token validity failure.

    Example:
        payload = verify_token(token)
        email   = payload["sub"]
        user_id = payload["user_id"]
        role    = payload["role"]
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token. Could not validate credentials.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Guard: ensure the token carries a "sub" (subject) claim
    if payload.get("sub") is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is missing the subject claim.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload
