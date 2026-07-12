"""
auth.py - Password Hashing

Handles bcrypt password operations via Passlib's CryptContext.

Responsibilities of this file:
  - hash_password(plain)          → bcrypt hash string
  - verify_password(plain, hash)  → bool

JWT operations have been intentionally separated into security.py so that:
  - auth.py  = synchronous, no HTTP context, pure crypto
  - security.py = JWT creation/verification, may raise HTTPExceptions

Re-exports for backward compatibility:
  Importing create_access_token or decode_access_token from auth.py still
  works — they are forwarded from security.py.
"""

import bcrypt

# Re-export JWT helpers from security.py so existing import paths keep working.
# New code should import directly from security.py for clarity.
from security import create_access_token, decode_access_token, verify_token  # noqa: F401


# ---------------------------------------------------------------------------
# Password Hashing (bcrypt via Passlib)
# ---------------------------------------------------------------------------

# Using bcrypt directly instead of passlib to support bcrypt >= 4.0.0


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.

    bcrypt is intentionally slow (work-factor based) to resist brute-force
    and dictionary attacks against a stolen password database.

    Args:
        plain_password: The raw password string from the registration request.

    Returns:
        A bcrypt hash string (60 chars) safe to store in the database.

    Security note:
        Never log or return this value in an API response.
    """
    pwd_bytes = plain_password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Compare a plaintext password against a stored bcrypt hash.

    Uses Passlib's constant-time comparison to prevent timing attacks.

    Args:
        plain_password:  The raw password from the login request.
        hashed_password: The bcrypt hash retrieved from the database.

    Returns:
        True if the password matches the hash, False otherwise.

    Security note:
        Always return a generic error to the user — never reveal whether
        the email or password was wrong (user enumeration prevention).
    """
    try:
        pwd_bytes = plain_password.encode('utf-8')
        hash_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(pwd_bytes, hash_bytes)
    except ValueError:
        return False
