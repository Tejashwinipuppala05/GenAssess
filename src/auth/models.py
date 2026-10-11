from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class UserRole(str, Enum):
    CANDIDATE = "CANDIDATE"
    RECRUITER = "RECRUITER"


@dataclass(frozen=True)
class User:
    id: int
    name: str
    email: str | None
    phone: str | None
    role: UserRole
    password_hash: str
    created_at: datetime
    updated_at: datetime


def user_from_row(row) -> User:
    stored_email = row["email"]
    return User(
        id=row["id"],
        name=row["name"],
        email=None if isinstance(stored_email, str) and stored_email.endswith("@phone.genassess.invalid") else stored_email,
        phone=row["phone"],
        role=UserRole(row["role"]),
        password_hash=row["password_hash"],
        created_at=datetime.fromisoformat(row["created_at"]),
        updated_at=datetime.fromisoformat(row["updated_at"]),
    )
