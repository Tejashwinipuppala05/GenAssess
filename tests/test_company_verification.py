from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from auth_api import app

FRONTEND_ORIGIN = "http://localhost:3000"
ORIGIN_HEADERS = {"Origin": FRONTEND_ORIGIN}
RECRUITER = {
    "name": "Test Recruiter",
    "email": "recruiter@example.com",
    "password": "correct horse battery staple",
    "role": "RECRUITER",
}
VERIFICATION = {
    "companyName": "Example Technologies Private Limited",
    "identifierType": "GSTIN",
    "identifier": "24ABKCS2033B1ZV",
    "websiteUrl": "https://example.com",
    "linkedinUrl": "https://www.linkedin.com/company/example",
}
JOB = {
    "title": "Senior Software Engineer",
    "description": "Build reliable software and collaborate with a cross-functional product team.",
    "location": "Bengaluru, India",
    "work_arrangement": "HYBRID",
}


@pytest.fixture
def recruiter_client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-at-least-32-bytes-long")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "verification.sqlite3"))
    monkeypatch.setenv("FRONTEND_ORIGIN", FRONTEND_ORIGIN)
    monkeypatch.setenv("COOKIE_SECURE", "false")
    monkeypatch.setenv("VERIFICATION_ADMIN_EMAILS", RECRUITER["email"])
    with TestClient(app) as client:
        registered = client.post("/auth/register", json=RECRUITER, headers=ORIGIN_HEADERS)
        assert registered.status_code == 201
        login = client.post("/auth/login", json=RECRUITER, headers=ORIGIN_HEADERS)
        assert login.status_code == 200
        yield client


def test_manual_admin_review_gates_job_posting(recruiter_client):
    client = recruiter_client
    blocked_job = client.post("/recruiter/jobs", json=JOB, headers=ORIGIN_HEADERS)
    submission = client.post(
        "/recruiter/company-verification",
        json=VERIFICATION,
        headers=ORIGIN_HEADERS,
    )
    current_user = client.get("/auth/me")
    queue = client.get("/admin/company-verifications")
    approved = client.post(
        f"/admin/company-verifications/{current_user.json()['id']}/review",
        json={"decision": "VERIFIED", "reviewer_note": "Registry and company profile match."},
        headers=ORIGIN_HEADERS,
    )
    published = client.post("/recruiter/jobs", json=JOB, headers=ORIGIN_HEADERS)
    listed = client.get("/recruiter/jobs")

    assert blocked_job.status_code == 403
    assert submission.status_code == 200
    assert submission.json()["status"] == "PENDING_REVIEW"
    assert submission.json()["registryStatus"] == "Manual review required"
    assert submission.json()["registryCompanyName"] is None
    assert submission.json()["identifier"].endswith("1ZV")
    assert queue.status_code == 200
    assert queue.json()[0]["identifier"] == VERIFICATION["identifier"]
    assert approved.status_code == 200
    assert approved.json()["status"] == "VERIFIED"
    assert published.status_code == 201
    assert listed.status_code == 200
    assert listed.json()[0]["title"] == JOB["title"]


def test_manual_submission_enters_review_queue_without_paid_registry_api(recruiter_client):
    client = recruiter_client
    response = client.post(
        "/recruiter/company-verification",
        json=VERIFICATION,
        headers=ORIGIN_HEADERS,
    )
    queue = client.get("/admin/company-verifications")

    assert response.status_code == 200
    assert response.json()["status"] == "PENDING_REVIEW"
    assert queue.json()[0]["companyName"] == VERIFICATION["companyName"]


def test_company_submission_validates_registry_id_and_linkedin_domain(recruiter_client):
    client = recruiter_client
    invalid_id = client.post(
        "/recruiter/company-verification",
        json={**VERIFICATION, "identifier": "not-a-gstin"},
        headers=ORIGIN_HEADERS,
    )
    invalid_linkedin = client.post(
        "/recruiter/company-verification",
        json={**VERIFICATION, "linkedinUrl": "https://example.com/company"},
        headers=ORIGIN_HEADERS,
    )

    assert invalid_id.status_code == 422
    assert invalid_linkedin.status_code == 422
