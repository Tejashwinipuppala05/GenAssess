from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field

from src.auth.schemas import UserResponse


class CandidateProfile(BaseModel):
    target_role: str | None = Field(default=None, serialization_alias="targetRole")

    model_config = ConfigDict(populate_by_name=True)


class CandidatePerformance(BaseModel):
    interviews_completed: int = Field(default=0, serialization_alias="interviewsCompleted")
    overall_score: float | None = Field(default=None, serialization_alias="overallScore")

    model_config = ConfigDict(populate_by_name=True)


class CandidateDashboardResponse(BaseModel):
    user: UserResponse
    profile: CandidateProfile
    previous_attempts: list[dict[str, object]] = Field(
        default_factory=list,
        serialization_alias="previousAttempts",
    )
    performance: CandidatePerformance
    recent_results: list[dict[str, object]] = Field(
        default_factory=list,
        serialization_alias="recentResults",
    )
    skill_overview: list[dict[str, object]] = Field(
        default_factory=list,
        serialization_alias="skillOverview",
    )

    model_config = ConfigDict(populate_by_name=True)


class RecruiterCompany(BaseModel):
    name: str | None = None


class RecruiterStatistics(BaseModel):
    total_interviews: int = Field(default=0, serialization_alias="totalInterviews")
    candidates_evaluated: int = Field(default=0, serialization_alias="candidatesEvaluated")
    average_score: float | None = Field(default=None, serialization_alias="averageScore")

    model_config = ConfigDict(populate_by_name=True)


class RecruiterDashboardResponse(BaseModel):
    user: UserResponse
    company: RecruiterCompany
    statistics: RecruiterStatistics
    created_interviews: list[dict[str, object]] = Field(
        default_factory=list,
        serialization_alias="createdInterviews",
    )
    candidate_results: list[dict[str, object]] = Field(
        default_factory=list,
        serialization_alias="candidateResults",
    )

    model_config = ConfigDict(populate_by_name=True)


class InterviewSetupPlaceholder(BaseModel):
    message: str
    user: UserResponse
