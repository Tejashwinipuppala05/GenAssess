from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.authorization import require_role
from src.auth.database import get_database
from src.auth.models import User, UserRole
from src.auth.routes import get_current_user, require_frontend_origin
from .schemas import (
    AdminCompanyVerificationResponse,
    CompanyVerificationResponse,
    CompanyVerificationReview,
    CompanyVerificationSubmission,
)

recruiter_router = APIRouter(prefix="/recruiter", tags=["company verification"])
admin_router = APIRouter(prefix="/admin", tags=["company verification review"])


def _private_response(row: sqlite3.Row) -> CompanyVerificationResponse:
    values = dict(row)
    values["identifier"] = f"****{values['identifier'][-4:]}"
    return CompanyVerificationResponse.model_validate(values)


def _require_admin(user: User) -> None:
    configured_emails = {
        email.strip().lower()
        for email in os.getenv("VERIFICATION_ADMIN_EMAILS", "").split(",")
        if email.strip()
    }
    if not configured_emails:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Company verification reviewers are not configured on this server.",
        )
    if not user.email or user.email.lower() not in configured_emails:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to review company verification requests.",
        )


def require_verified_company(user: User, connection: sqlite3.Connection) -> None:
    row = connection.execute(
        "SELECT status FROM company_verifications WHERE user_id = ?",
        (user.id,),
    ).fetchone()
    if row is None or row["status"] != "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Company verification must be approved before publishing a job.",
        )


@recruiter_router.get(
    "/company-verification",
    response_model=CompanyVerificationResponse,
)
def get_company_verification(
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> CompanyVerificationResponse:
    row = connection.execute(
        "SELECT * FROM company_verifications WHERE user_id = ?",
        (user.id,),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Company verification has not been submitted.",
        )
    return _private_response(row)


@recruiter_router.post(
    "/company-verification",
    response_model=CompanyVerificationResponse,
    dependencies=[Depends(require_frontend_origin)],
)
def submit_company_verification(
    payload: CompanyVerificationSubmission,
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> CompanyVerificationResponse:
    existing = connection.execute(
        "SELECT status FROM company_verifications WHERE user_id = ?",
        (user.id,),
    ).fetchone()
    if existing is not None and existing["status"] == "VERIFIED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This company is already verified. Contact support if its details have changed.",
        )

    now = datetime.now(timezone.utc).isoformat()
    registry_status = "Manual review required"
    registry_name = None
    request_status = "PENDING_REVIEW"
    connection.execute(
        """
        INSERT INTO company_verifications (
            user_id, company_name, identifier_type, identifier, website_url, linkedin_url,
            registry_status, registry_company_name, status, reviewer_note, reviewed_at,
            created_at, updated_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            company_name = excluded.company_name,
            identifier_type = excluded.identifier_type,
            identifier = excluded.identifier,
            website_url = excluded.website_url,
            linkedin_url = excluded.linkedin_url,
            registry_status = excluded.registry_status,
            registry_company_name = excluded.registry_company_name,
            status = excluded.status,
            reviewer_note = NULL,
            reviewed_at = NULL,
            updated_at = excluded.updated_at
        """,
        (
            user.id,
            payload.company_name,
            payload.identifier_type,
            payload.identifier,
            str(payload.website_url),
            str(payload.linkedin_url),
            registry_status,
            registry_name,
            request_status,
            now,
            now,
        ),
    )
    connection.commit()
    row = connection.execute(
        "SELECT * FROM company_verifications WHERE user_id = ?",
        (user.id,),
    ).fetchone()
    return _private_response(row)


@admin_router.get(
    "/company-verifications",
    response_model=list[AdminCompanyVerificationResponse],
)
def list_company_verifications(
    user: Annotated[User, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> list[AdminCompanyVerificationResponse]:
    _require_admin(user)
    rows = connection.execute(
        """
        SELECT
            verification.*,
            users.name AS user_name,
            CASE
                WHEN users.email LIKE '%@phone.genassess.invalid' THEN NULL
                ELSE users.email
            END AS user_email,
            users.phone AS user_phone
        FROM company_verifications AS verification
        JOIN users ON users.id = verification.user_id
        WHERE verification.status = 'PENDING_REVIEW'
        ORDER BY verification.updated_at ASC
        LIMIT 100
        """
    ).fetchall()
    return [AdminCompanyVerificationResponse.model_validate(dict(row)) for row in rows]


@admin_router.post(
    "/company-verifications/{user_id}/review",
    response_model=AdminCompanyVerificationResponse,
    dependencies=[Depends(require_frontend_origin)],
)
def review_company_verification(
    user_id: int,
    payload: CompanyVerificationReview,
    user: Annotated[User, Depends(get_current_user)],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> AdminCompanyVerificationResponse:
    _require_admin(user)
    now = datetime.now(timezone.utc).isoformat()
    cursor = connection.execute(
        """
        UPDATE company_verifications
        SET status = ?, reviewer_note = ?, reviewed_at = ?, updated_at = ?
        WHERE user_id = ? AND status = 'PENDING_REVIEW'
        """,
        (payload.decision, payload.reviewer_note, now, now, user_id),
    )
    if cursor.rowcount == 0:
        exists = connection.execute(
            "SELECT 1 FROM company_verifications WHERE user_id = ?",
            (user_id,),
        ).fetchone()
        if exists is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Company verification request was not found.",
            )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending company verification requests can be reviewed.",
        )
    connection.commit()
    row = connection.execute(
        """
        SELECT
            verification.*,
            users.name AS user_name,
            CASE
                WHEN users.email LIKE '%@phone.genassess.invalid' THEN NULL
                ELSE users.email
            END AS user_email,
            users.phone AS user_phone
        FROM company_verifications AS verification
        JOIN users ON users.id = verification.user_id
        WHERE verification.user_id = ?
        """,
        (user_id,),
    ).fetchone()
    return AdminCompanyVerificationResponse.model_validate(dict(row))
