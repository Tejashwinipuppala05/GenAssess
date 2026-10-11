from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends

from src.auth.authorization import require_role
from src.auth.models import User, UserRole
from .schemas import (
    CandidateDashboardResponse,
    InterviewSetupPlaceholder,
    RecruiterDashboardResponse,
)

candidate_router = APIRouter(prefix="/candidate", tags=["candidate dashboard"])
recruiter_router = APIRouter(prefix="/recruiter", tags=["recruiter dashboard"])


@candidate_router.get(
    "/dashboard",
    response_model=CandidateDashboardResponse,
)
def candidate_dashboard(
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
) -> CandidateDashboardResponse:
    return CandidateDashboardResponse(user=user, profile={}, performance={})


@candidate_router.get(
    "/interview/setup",
    response_model=InterviewSetupPlaceholder,
)
def interview_setup_placeholder(
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
) -> InterviewSetupPlaceholder:
    return InterviewSetupPlaceholder(
        message="Interview setup will be implemented in the next feature.",
        user=user,
    )


@recruiter_router.get(
    "/dashboard",
    response_model=RecruiterDashboardResponse,
)
def recruiter_dashboard(
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
) -> RecruiterDashboardResponse:
    return RecruiterDashboardResponse(user=user, company={}, statistics={})


@recruiter_router.get(
    "/interviews/new",
    response_model=InterviewSetupPlaceholder,
)
def recruiter_interview_placeholder(
    user: Annotated[User, Depends(require_role(UserRole.RECRUITER))],
) -> InterviewSetupPlaceholder:
    return InterviewSetupPlaceholder(
        message="Recruiter interview creation will be implemented in a later feature.",
        user=user,
    )
