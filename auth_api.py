from __future__ import annotations

import os
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from src.auth.database import initialize_database
from src.auth.routes import router as auth_router
from src.auth.security import jwt_secret, token_lifetime
from src.dashboard.routes import candidate_router, recruiter_router
from src.verification.routes import admin_router as verification_admin_router
from src.verification.routes import recruiter_router as verification_recruiter_router
from src.verification.jobs import router as recruiter_jobs_router
from src.rounds.routes import router as candidate_rounds_router
from src.applications import candidate_router as applications_candidate_router, recruiter_router as applications_recruiter_router
from src.technical.routes import router as candidate_technical_router



from src.aptitude.routes import router as candidate_aptitude_router

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    jwt_secret()
    token_lifetime()
    initialize_database()
    yield


app = FastAPI(title="GenAssess Authentication API", version="1.0.0", lifespan=lifespan)
frontend_origin = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000").rstrip("/")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(recruiter_router)
app.include_router(verification_recruiter_router)
app.include_router(verification_admin_router)
app.include_router(recruiter_jobs_router)
app.include_router(candidate_aptitude_router)
app.include_router(applications_candidate_router)
app.include_router(applications_recruiter_router)
app.include_router(candidate_rounds_router)
app.include_router(candidate_technical_router)
