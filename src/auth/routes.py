from __future__ import annotations

import os
import secrets
import sqlite3
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Annotated

import jwt
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import JSONResponse

from .database import get_database
from .models import User, UserRole, user_from_row
from .schemas import (
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    SupabaseExchangeRequest,
    UserResponse,
)
from .security import (
    DUMMY_PASSWORD_HASH,
    create_session_token,
    decode_session_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["authentication"])
COOKIE_NAME = "genassess_session"


def require_frontend_origin(request: Request) -> None:
    expected_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").rstrip("/")
    if request.headers.get("origin", "").rstrip("/") != expected_origin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Request origin is not allowed.")


def set_session_cookie(response: Response, token: str, expires_at: datetime) -> None:
    max_age = max(0, int((expires_at - datetime.now(timezone.utc)).total_seconds()))
    response.set_cookie(
        key=COOKIE_NAME,
        value=token,
        max_age=max_age,
        expires=max_age,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "true").lower() == "true",
        samesite="lax",
        path="/",
    )


def get_current_user(
    request: Request,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> User:
    token = request.cookies.get(COOKIE_NAME)
    if not token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    try:
        claims = decode_session_token(token)
        user_id = int(str(claims["sub"]))
        token_id = str(claims["jti"])
    except (jwt.InvalidTokenError, KeyError, TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.") from None

    session = connection.execute(
        """
        SELECT user_id
        FROM user_sessions
        WHERE token_id = ? AND user_id = ? AND revoked_at IS NULL AND expires_at > ?
        """,
        (token_id, user_id, int(datetime.now(timezone.utc).timestamp())),
    ).fetchone()
    if session is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")

    user_row = connection.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
    if user_row is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication required.")
    return user_from_row(user_row)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_frontend_origin)],
)
def register(
    payload: RegisterRequest,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> UserResponse:
    email = str(payload.email).lower()
    existing = connection.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="An account with this email already exists.")
    if payload.phone and connection.execute(
        "SELECT 1 FROM users WHERE phone = ?",
        (payload.phone,),
    ).fetchone():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this mobile number already exists.",
        )

    now = datetime.now(timezone.utc).isoformat()
    try:
        cursor = connection.execute(
            """
            INSERT INTO users (name, email, phone, role, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.name,
                email,
                payload.phone,
                payload.role.value,
                hash_password(payload.password),
                now,
                now,
            ),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        connection.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email or mobile number already exists.",
        ) from None

    row = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return UserResponse.model_validate(user_from_row(row))


@router.post(
    "/supabase/exchange",
    response_model=LoginResponse,
    dependencies=[Depends(require_frontend_origin)],
)
def exchange_supabase_token(
    payload: SupabaseExchangeRequest,
    response: Response,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> LoginResponse:
    supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
    anon_key = os.getenv("SUPABASE_ANON_KEY", "")
    if not supabase_url or not anon_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Google sign-in is not configured on this server.",
        )

    request = urllib.request.Request(
        f"{supabase_url}/auth/v1/user",
        headers={
            "apikey": anon_key,
            "Authorization": f"Bearer {payload.access_token}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(request, timeout=8) as provider_response:
            provider_user = json.loads(provider_response.read())
    except urllib.error.HTTPError as exc:
        if exc.code in (400, 401, 403):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="The external sign-in session is invalid or expired.",
            ) from None
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The external identity provider could not verify this session.",
        ) from None
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, UnicodeDecodeError):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The external identity provider could not be reached.",
        ) from None

    if not isinstance(provider_user, dict) or not isinstance(provider_user.get("id"), str):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="The external identity provider returned an invalid user response.",
        )

    email_value = provider_user.get("email")
    email = email_value.strip().lower() if isinstance(email_value, str) else None
    phone_value = provider_user.get("phone")
    phone = phone_value.strip() if isinstance(phone_value, str) and phone_value.strip() else None
    verified_email = bool(provider_user.get("email_confirmed_at"))
    if not (email and verified_email):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Google sign-in requires a verified email address.",
        )

    provider_id = provider_user["id"]
    row = connection.execute(
        "SELECT * FROM users WHERE supabase_user_id = ?",
        (provider_id,),
    ).fetchone()
    if row is None:
        if email and connection.execute("SELECT 1 FROM users WHERE email = ?", (email,)).fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email already exists. Sign in with its original method first.",
            )
        if phone and connection.execute("SELECT 1 FROM users WHERE phone = ?", (phone,)).fetchone():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this phone number already exists.",
            )

        metadata = provider_user.get("user_metadata")
        metadata = metadata if isinstance(metadata, dict) else {}
        display_name = next(
            (
                metadata.get(field)
                for field in ("full_name", "name", "display_name")
                if isinstance(metadata.get(field), str) and metadata[field].strip()
            ),
            phone or email or "GenAssess user",
        )
        now = datetime.now(timezone.utc).isoformat()
        cursor = connection.execute(
            """
            INSERT INTO users (
                name, email, phone, supabase_user_id, role, password_hash, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                display_name[:100],
                email or f"{provider_id}@phone.genassess.invalid",
                phone,
                provider_id,
                payload.role.value,
                hash_password(secrets.token_urlsafe(48)),
                now,
                now,
            ),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM users WHERE id = ?", (cursor.lastrowid,)).fetchone()
    elif email and row["email"] is None:
        connection.execute(
            "UPDATE users SET email = ?, updated_at = ? WHERE id = ?",
            (email, datetime.now(timezone.utc).isoformat(), row["id"]),
        )
        connection.commit()
        row = connection.execute("SELECT * FROM users WHERE id = ?", (row["id"],)).fetchone()

    user = user_from_row(row)
    token, token_id, expires_at = create_session_token(user)
    connection.execute(
        """
        INSERT INTO user_sessions (token_id, user_id, expires_at, revoked_at, created_at)
        VALUES (?, ?, ?, NULL, ?)
        """,
        (
            token_id,
            user.id,
            int(expires_at.timestamp()),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    set_session_cookie(response, token, expires_at)
    return LoginResponse(user=UserResponse.model_validate(user), expires_at=expires_at)


@router.post(
    "/login",
    response_model=LoginResponse,
    dependencies=[Depends(require_frontend_origin)],
)
def login(
    payload: LoginRequest,
    response: Response,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> LoginResponse:
    email = str(payload.email).lower()
    row = connection.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
    if row is None:
        verify_password(payload.password, DUMMY_PASSWORD_HASH)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")
    if not verify_password(payload.password, row["password_hash"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Email or password is incorrect.")

    user = user_from_row(row)
    token, token_id, expires_at = create_session_token(user)
    connection.execute(
        """
        INSERT INTO user_sessions (token_id, user_id, expires_at, revoked_at, created_at)
        VALUES (?, ?, ?, NULL, ?)
        """,
        (
            token_id,
            user.id,
            int(expires_at.timestamp()),
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    set_session_cookie(response, token, expires_at)
    return LoginResponse(user=UserResponse.model_validate(user), expires_at=expires_at)


@router.get("/me", response_model=UserResponse)
def current_user(user: Annotated[User, Depends(get_current_user)]) -> UserResponse:
    return UserResponse.model_validate(user)


@router.post("/logout", dependencies=[Depends(require_frontend_origin)])
def logout(
    request: Request,
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> JSONResponse:
    token = request.cookies.get(COOKIE_NAME)
    if token:
        try:
            claims = decode_session_token(token)
        except jwt.InvalidTokenError:
            claims = {}
        token_id = claims.get("jti")
        if isinstance(token_id, str):
            connection.execute(
                "UPDATE user_sessions SET revoked_at = ? WHERE token_id = ? AND revoked_at IS NULL",
                (int(datetime.now(timezone.utc).timestamp()), token_id),
            )
            connection.commit()

    logout_response = JSONResponse(status_code=status.HTTP_200_OK, content={"message": "Logged out."})
    logout_response.delete_cookie(
        key=COOKIE_NAME,
        httponly=True,
        secure=os.getenv("COOKIE_SECURE", "true").lower() == "true",
        samesite="lax",
        path="/",
    )
    return logout_response
