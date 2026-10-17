"""Хеширование паролей и работа с JWT."""

import hashlib
import hmac
import secrets
from datetime import UTC, datetime

import jwt

from .config import ACCESS_TOKEN_TTL, ALGORITHM, SECRET_KEY

_PBKDF2_ITERATIONS = 200_000


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _PBKDF2_ITERATIONS)
    return f"{salt.hex()}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    salt_hex, digest_hex = stored.split("$")
    digest = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), bytes.fromhex(salt_hex), _PBKDF2_ITERATIONS
    )
    return hmac.compare_digest(digest.hex(), digest_hex)


def create_access_token(subject: str) -> str:
    now = datetime.now(UTC)
    payload = {"sub": subject, "iat": now, "exp": now + ACCESS_TOKEN_TTL}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def decode_access_token(token: str) -> str:
    """Возвращает subject токена или бросает jwt.InvalidTokenError."""
    payload = jwt.decode(
        token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["sub", "exp"]}
    )
    return payload["sub"]
