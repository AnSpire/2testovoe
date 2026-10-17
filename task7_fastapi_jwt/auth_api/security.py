import hashlib
import hmac
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import StrEnum

import jwt

from .config import ACCESS_TOKEN_TTL, ALGORITHM, PRIVATE_KEY, PUBLIC_KEY, REFRESH_TOKEN_TTL

_PBKDF2_ITERATIONS = 200_000


class TokenType(StrEnum):
    ACCESS = "access"
    REFRESH = "refresh"


@dataclass(frozen=True)
class TokenClaims:
    sub: str
    sid: str
    jti: str


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


def new_token_id() -> str:
    return secrets.token_hex(16)


def _encode(subject: str, session_id: str, token_type: TokenType, ttl: timedelta, jti: str) -> str:
    now = datetime.now(UTC)
    payload = {
        "sub": subject,
        "sid": session_id,
        "type": token_type,
        "jti": jti,
        "iat": now,
        "exp": now + ttl,
    }
    return jwt.encode(payload, PRIVATE_KEY, algorithm=ALGORITHM)


def create_token_pair(subject: str, session_id: str, refresh_jti: str) -> tuple[str, str]:
    access = _encode(subject, session_id, TokenType.ACCESS, ACCESS_TOKEN_TTL, new_token_id())
    refresh = _encode(subject, session_id, TokenType.REFRESH, REFRESH_TOKEN_TTL, refresh_jti)
    return access, refresh


def decode_token(token: str, expected_type: TokenType) -> TokenClaims:
    payload = jwt.decode(
        token,
        PUBLIC_KEY,
        algorithms=[ALGORITHM],
        options={"require": ["sub", "sid", "jti", "type", "exp"]},
    )
    if payload["type"] != expected_type:
        raise jwt.InvalidTokenError("Неверный тип токена")
    return TokenClaims(payload["sub"], payload["sid"], payload["jti"])
