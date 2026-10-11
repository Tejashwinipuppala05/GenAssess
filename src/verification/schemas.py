from __future__ import annotations

import re
from typing import Literal
from urllib.parse import urlparse

from pydantic import BaseModel, ConfigDict, Field, HttpUrl, field_validator, model_validator


class CompanyVerificationSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    company_name: str = Field(min_length=2, max_length=200, alias="companyName")
    identifier_type: Literal["CIN", "GSTIN"] = Field(alias="identifierType")
    identifier: str = Field(min_length=15, max_length=21)
    website_url: HttpUrl = Field(alias="websiteUrl")
    linkedin_url: HttpUrl = Field(alias="linkedinUrl")

    @field_validator("company_name")
    @classmethod
    def validate_company_name(cls, value: str) -> str:
        value = value.strip()
        if not value or any(ord(character) < 32 for character in value):
            raise ValueError("Enter a valid registered company name.")
        return value

    @field_validator("identifier")
    @classmethod
    def normalize_identifier(cls, value: str) -> str:
        return re.sub(r"\s+", "", value).upper()

    @field_validator("website_url", mode="before")
    @classmethod
    def require_http_website(cls, value: object) -> object:
        if isinstance(value, str) and not value.startswith(("https://", "http://")):
            raise ValueError("Enter a website URL beginning with https:// or http://.")
        return value

    @field_validator("linkedin_url")
    @classmethod
    def require_linkedin_url(cls, value: HttpUrl) -> HttpUrl:
        host = urlparse(str(value)).hostname or ""
        if host != "linkedin.com" and not host.endswith(".linkedin.com"):
            raise ValueError("Enter a company LinkedIn URL.")
        return value

    @model_validator(mode="after")
    def validate_identifier_format(self) -> CompanyVerificationSubmission:
        if self.identifier_type == "CIN" and not re.fullmatch(
            r"[LU]\d{5}[A-Z]{2}\d{4}[A-Z]{3}\d{6}",
            self.identifier,
        ):
            raise ValueError("Enter a valid 21-character CIN.")
        if self.identifier_type == "GSTIN" and not re.fullmatch(
            r"\d{2}[A-Z]{5}\d{4}[A-Z][1-9A-Z]Z[0-9A-Z]",
            self.identifier,
        ):
            raise ValueError("Enter a valid 15-character GSTIN.")
        return self


class CompanyVerificationResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    company_name: str = Field(serialization_alias="companyName")
    identifier_type: str = Field(serialization_alias="identifierType")
    identifier: str
    website_url: str = Field(serialization_alias="websiteUrl")
    linkedin_url: str = Field(serialization_alias="linkedinUrl")
    registry_status: str = Field(serialization_alias="registryStatus")
    registry_company_name: str | None = Field(serialization_alias="registryCompanyName")
    status: str
    reviewer_note: str | None = Field(serialization_alias="reviewerNote")
    reviewed_at: str | None = Field(serialization_alias="reviewedAt")
    updated_at: str = Field(serialization_alias="updatedAt")


class AdminCompanyVerificationResponse(CompanyVerificationResponse):
    user_id: int = Field(serialization_alias="userId")
    user_name: str = Field(serialization_alias="userName")
    user_email: str | None = Field(serialization_alias="userEmail")
    user_phone: str | None = Field(serialization_alias="userPhone")


class CompanyVerificationReview(BaseModel):
    model_config = ConfigDict(extra="forbid")

    decision: Literal["VERIFIED", "REJECTED"]
    reviewer_note: str = Field(min_length=5, max_length=1000)

    @field_validator("reviewer_note")
    @classmethod
    def normalize_note(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("Provide a review note.")
        return value
