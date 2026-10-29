from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.auth.authorization import require_role
from src.auth.database import get_database
from src.auth.models import User, UserRole

candidate_router = APIRouter(prefix="/candidate", tags=["candidate applications"])
recruiter_router = APIRouter(prefix="/recruiter", tags=["recruiter applicants"])


class ApplicationResponse(BaseModel):
    id: int
    jobId: int = Field(serialization_alias="jobId")
    candidateId: int = Field(serialization_alias="candidateId")
    status: str
    score: int | None
    notes: str | None
    createdAt: str = Field(serialization_alias="createdAt")
    updatedAt: str = Field(serialization_alias="updatedAt")

    model_config = ConfigDict(populate_by_name=True)


class EvaluateApplicationRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    score: int = Field(ge=0, le=100)
    notes: str | None = None
    status: str = "REVIEWED"


@candidate_router.post("/jobs/{job_id}/apply", response_model=ApplicationResponse)
def apply_to_job(
    job_id: int,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> ApplicationResponse:
    job = connection.execute("SELECT id FROM job_posts WHERE id = ?", (job_id,)).fetchone()
    if job is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    now = datetime.now(timezone.utc).isoformat()
    try:
        cursor = connection.execute(
            """
            INSERT INTO job_applications (job_id, candidate_id, status, created_at, updated_at)
            VALUES (?, ?, 'APPLIED', ?, ?)
            """,
            (job_id, user.id, now, now),
        )
        connection.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Already applied to this job.")
    row = connection.execute("SELECT * FROM job_applications WHERE id = ?", (cursor.lastrowid,)).fetchone()
    return _to_response(row)


@candidate_router.get("/applications", response_model=list[ApplicationResponse])
def my_applications(
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> list[ApplicationResponse]:
    rows = connection.execute(
        "SELECT * FROM job_applications WHERE candidate_id = ? ORDER BY created_at DESC",
        (user.id,),
    ).fetchall()
    return [_to_response(row) for row in rows]


@recruiter_router.get("/jobs/{job_id}/applicants", response_model=list[ApplicationResponse])
def job_applicants(
    job_id: int,
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> list[ApplicationResponse]:
    job = connection.execute("SELECT id, recruiter_id FROM job_posts WHERE id = ?", (job_id,)).fetchone()
    if job is None or job["recruiter_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found.")
    rows = connection.execute(
        "SELECT * FROM job_applications WHERE job_id = ? ORDER BY created_at DESC",
        (job_id,),
    ).fetchall()
    return [_to_response(row) for row in rows]


@recruiter_router.post("/applications/{application_id}/evaluate", response_model=ApplicationResponse)
def evaluate_application(
    application_id: int,
    payload: EvaluateApplicationRequest,
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> ApplicationResponse:
    row = connection.execute(
        """
        SELECT ja.*, jp.recruiter_id
        FROM job_applications ja
        JOIN job_posts jp ON jp.id = ja.job_id
        WHERE ja.id = ?
        """,
        (application_id,),
    ).fetchone()
    if row is None or row["recruiter_id"] != user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Application not found.")
    now = datetime.now(timezone.utc).isoformat()
    connection.execute(
        """
        UPDATE job_applications
        SET status = ?, score = ?, notes = ?, updated_at = ?
        WHERE id = ?
        """,
        (payload.status, payload.score, payload.notes, now, application_id),
    )
    connection.commit()
    updated = connection.execute("SELECT * FROM job_applications WHERE id = ?", (application_id,)).fetchone()
    return _to_response(updated)


def _to_response(row: sqlite3.Row) -> ApplicationResponse:
    return ApplicationResponse(
        id=row["id"],
        jobId=row["job_id"],
        candidateId=row["candidate_id"],
        status=row["status"],
        score=row["score"],
        notes=row["notes"],
        createdAt=row["created_at"],
        updatedAt=row["updated_at"],
    )

@candidate_router.get("/jobs", response_model=list[dict])
def list_jobs(connection: Annotated[sqlite3.Connection, Depends(get_database)]) -> list[dict]:
    rows = connection.execute(
        "SELECT id, title, description, location, work_arrangement, created_at FROM job_posts ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]
