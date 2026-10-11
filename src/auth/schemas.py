from __future__ import annotations

import re
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from .models import UserRole


class RegisterRequest(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=False, extra="forbid")

    name: str = Field(min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(min_length=12, max_length=128)
    role: UserRole = UserRole.CANDIDATE
    phone: str | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value: str) -> str:
        value = value.strip()
        if not value or any(ord(character) < 32 for character in value):
            raise ValueError("Enter a valid name.")
        return value

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        normalized = re.sub(r"[\s()-]", "", value)
        if not normalized.startswith("+") or not normalized[1:].isdigit():
            raise ValueError("Enter a mobile number in international format, such as +919876543210.")
        if not 8 <= len(normalized[1:]) <= 15:
            raise ValueError("Enter a valid international mobile number.")
        return normalized


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value: object) -> object:
        return value.strip().lower() if isinstance(value, str) else value


class SupabaseExchangeRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str = Field(min_length=1, max_length=8192)
    role: UserRole = UserRole.CANDIDATE


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    name: str
    email: EmailStr | None
    phone: str | None = None
    role: UserRole
    created_at: datetime = Field(serialization_alias="createdAt")
    updated_at: datetime = Field(serialization_alias="updatedAt")


class LoginResponse(BaseModel):
    user: UserResponse
    expires_at: datetime = Field(serialization_alias="expiresAt")
