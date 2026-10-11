from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field, field_validator

from src.auth.authorization import require_role
from src.auth.database import get_database
from src.auth.models import User, UserRole
from src.auth.routes import require_frontend_origin
from .routes import require_verified_company

router = APIRouter(prefix="/recruiter/jobs", tags=["recruiter jobs"])


class JobPostSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(min_length=5, max_length=150)
    description: str = Field(min_length=30, max_length=10000)
    location: str = Field(min_length=2, max_length=150)
    work_arrangement: Literal["REMOTE", "HYBRID", "ONSITE"]

    @field_validator("title", "description", "location")
    @classmethod
    def clean_required_text(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("This field cannot be blank.")
        return value


class JobPostResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    title: str
    description: str
    location: str
    work_arrangement: str = Field(serialization_alias="workArrangement")
    created_at: datetime = Field(serialization_alias="createdAt")


@router.get("", response_model=list[JobPostResponse])
def list_job_posts(
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> list[JobPostResponse]:
    rows = connection.execute(
        """
        SELECT id, title, description, location, work_arrangement, created_at
        FROM job_posts
        WHERE recruiter_id = ?
        ORDER BY id DESC
        """,
        (user.id,),
    ).fetchall()
    return [JobPostResponse.model_validate(dict(row)) for row in rows]


@router.post(
    "",
    response_model=JobPostResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_frontend_origin)],
)
def create_job_post(
    payload: JobPostSubmission,
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> JobPostResponse:
    require_verified_company(user, connection)
    cursor = connection.execute(
        """
        INSERT INTO job_posts (
            recruiter_id, title, description, location, work_arrangement, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            user.id,
            payload.title,
            payload.description,
            payload.location,
            payload.work_arrangement,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    connection.commit()
    row = connection.execute(
        """
        SELECT id, title, description, location, work_arrangement, created_at
        FROM job_posts WHERE id = ?
        """,
        (cursor.lastrowid,),
    ).fetchone()
    return JobPostResponse.model_validate(dict(row))
