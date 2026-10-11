from __future__ import annotations

import os
import secrets
import uuid
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash
from pwdlib.exceptions import UnknownHashError

from .models import User

password_hash = PasswordHash.recommended()
DUMMY_PASSWORD_HASH = password_hash.hash(secrets.token_urlsafe(32))
JWT_ISSUER = "genassess"
JWT_ALGORITHM = "HS256"


def jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET", "")
    if len(secret.encode("utf-8")) < 32:
        raise RuntimeError("JWT_SECRET must contain at least 32 bytes.")
    return secret


def token_lifetime() -> timedelta:
    try:
        minutes = int(os.getenv("ACCESS_TOKEN_TTL_MINUTES", "10080"))
    except ValueError as exc:
        raise RuntimeError("ACCESS_TOKEN_TTL_MINUTES must be a positive integer.") from exc
    if not 1 <= minutes <= 43200:
        raise RuntimeError("ACCESS_TOKEN_TTL_MINUTES must be between 1 and 43200.")
    return timedelta(minutes=minutes)


def create_session_token(user: User) -> tuple[str, str, datetime]:
    now = datetime.now(timezone.utc)
    expires_at = now + token_lifetime()
    token_id = str(uuid.uuid4())
    claims = {
        "sub": str(user.id),
        "jti": token_id,
        "iss": JWT_ISSUER,
        "iat": now,
        "exp": expires_at,
    }
    token = jwt.encode(claims, jwt_secret(), algorithm=JWT_ALGORITHM)
    return token, token_id, expires_at


def decode_session_token(token: str) -> dict[str, object]:
    return jwt.decode(
        token,
        jwt_secret(),
        algorithms=[JWT_ALGORITHM],
        issuer=JWT_ISSUER,
        options={"require": ["sub", "jti", "iss", "iat", "exp"]},
    )


def verify_password(plain_password: str, stored_hash: str) -> bool:
    try:
        return password_hash.verify(plain_password, stored_hash)
    except (UnknownHashError, ValueError, TypeError):
        return False


def hash_password(plain_password: str) -> str:
    return password_hash.hash(plain_password)
