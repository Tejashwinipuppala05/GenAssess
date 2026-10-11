from __future__ import annotations

import sqlite3
import sys
from concurrent.futures import ThreadPoolExecutor
import json

from fastapi.testclient import TestClient

from auth_api import app
from src.auth.routes import COOKIE_NAME
from src.auth.database import get_database
from src.auth.security import verify_password

FRONTEND_ORIGIN = "http://localhost:3000"
ORIGIN_HEADERS = {"Origin": FRONTEND_ORIGIN}
VALID_USER = {
    "name": "Test Candidate",
    "email": "candidate@example.com",
    "password": "correct horse battery staple",
}


def make_client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-at-least-32-bytes-long")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "auth.sqlite3"))
    monkeypatch.setenv("FRONTEND_ORIGIN", FRONTEND_ORIGIN)
    monkeypatch.setenv("COOKIE_SECURE", "false")
    return TestClient(app)


def test_database_connection_can_be_used_by_fastapi_worker_thread(monkeypatch, tmp_path):
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "threaded.sqlite3"))
    database = get_database()
    connection = next(database)

    with ThreadPoolExecutor(max_workers=1) as executor:
        result = executor.submit(lambda: connection.execute("SELECT 1").fetchone()[0]).result()

    try:
        assert result == 1
    finally:
        database.close()


def test_register_creates_safe_user_and_persists_hash(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == VALID_USER["name"]
    assert body["email"] == VALID_USER["email"]
    assert "password" not in body
    assert "password_hash" not in body
    assert "createdAt" in body

    connection = sqlite3.connect(tmp_path / "auth.sqlite3")
    stored_hash = connection.execute("SELECT password_hash FROM users").fetchone()[0]
    connection.close()
    assert stored_hash != VALID_USER["password"]


def test_registration_defaults_to_candidate_and_login_returns_role(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        registered = client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)
        login = client.post("/auth/login", json=VALID_USER, headers=ORIGIN_HEADERS)
        current = client.get("/auth/me")

    assert registered.status_code == 201
    assert registered.json()["role"] == "CANDIDATE"
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "CANDIDATE"
    assert current.status_code == 200
    assert current.json()["role"] == "CANDIDATE"


def test_registration_can_choose_recruiter_role(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/auth/register",
            json={**VALID_USER, "role": "RECRUITER"},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 201
    assert response.json()["role"] == "RECRUITER"


def test_registration_saves_optional_international_phone_number(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/auth/register",
            json={**VALID_USER, "phone": "+91 98765 43210"},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 201
    assert response.json()["phone"] == "+919876543210"


def test_registration_rejects_invalid_optional_phone_number(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/auth/register",
            json={**VALID_USER, "phone": "not a phone number"},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 422


def test_supabase_phone_only_exchange_is_disabled_to_avoid_paid_sms_auth(
    monkeypatch,
    tmp_path,
):
    monkeypatch.setenv("SUPABASE_URL", "https://project.example")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")

    class ProviderResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps(
                {
                    "id": "phone-user-123",
                    "phone": "+919876543210",
                    "phone_confirmed_at": "2026-01-01T00:00:00Z",
                    "user_metadata": {"name": "Phone Recruiter"},
                }
            ).encode()

    monkeypatch.setattr("src.auth.routes.urllib.request.urlopen", lambda *_args, **_kwargs: ProviderResponse())
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/auth/supabase/exchange",
            json={"access_token": "provider-access-token", "role": "RECRUITER"},
            headers=ORIGIN_HEADERS,
        )
        current = client.get("/auth/me")

    assert response.status_code == 403
    assert "verified email" in response.json()["detail"]
    assert current.status_code == 401


def test_supabase_exchange_rejects_existing_local_email_account(monkeypatch, tmp_path):
    monkeypatch.setenv("SUPABASE_URL", "https://project.example")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "test-anon-key")

    class ProviderResponse:
        def __enter__(self):
            return self

        def __exit__(self, *_args):
            return None

        def read(self):
            return json.dumps(
                {
                    "id": "google-user-123",
                    "email": VALID_USER["email"],
                    "email_confirmed_at": "2026-01-01T00:00:00Z",
                    "user_metadata": {"name": "Local Candidate"},
                }
            ).encode()

    monkeypatch.setattr("src.auth.routes.urllib.request.urlopen", lambda *_args, **_kwargs: ProviderResponse())
    with make_client(monkeypatch, tmp_path) as client:
        client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)
        response = client.post(
            "/auth/supabase/exchange",
            json={"access_token": "provider-access-token", "role": "CANDIDATE"},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 409


def test_register_rejects_duplicate_email_without_case_sensitivity(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        first = client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)
        duplicate = client.post(
            "/auth/register",
            json={**VALID_USER, "email": "CANDIDATE@example.com"},
            headers=ORIGIN_HEADERS,
        )

    assert first.status_code == 201
    assert duplicate.status_code == 409


def test_register_validates_inputs(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/auth/register",
            json={**VALID_USER, "email": "not-an-email", "password": "short"},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 422


def test_invalid_stored_password_hash_does_not_authenticate():
    assert verify_password("some password", "not-a-valid-password-hash") is False


def test_login_rejects_wrong_password_without_disclosing_account_state(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)
        response = client.post(
            "/auth/login",
            json={**VALID_USER, "password": "wrong password"},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email or password is incorrect."


def test_login_rejects_unknown_email_with_same_error(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post(
            "/auth/login",
            json={"email": "unknown@example.com", "password": VALID_USER["password"]},
            headers=ORIGIN_HEADERS,
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Email or password is incorrect."


def test_login_me_and_logout_revoke_session(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)

        login = client.post("/auth/login", json=VALID_USER, headers=ORIGIN_HEADERS)
        assert login.status_code == 200
        assert "token" not in login.json()
        cookie = login.cookies.get(COOKIE_NAME)
        assert cookie
        assert "httponly" in login.headers["set-cookie"].lower()

        authenticated = client.get("/auth/me")
        assert authenticated.status_code == 200
        assert authenticated.json()["email"] == VALID_USER["email"]

        logout = client.post("/auth/logout", headers=ORIGIN_HEADERS)
        assert logout.status_code == 200
        assert client.get("/auth/me").status_code == 401

        client.cookies.set(COOKIE_NAME, cookie)
        revoked_session = client.get("/auth/me")
        assert revoked_session.status_code == 401


def test_protected_route_rejects_missing_or_invalid_cookie(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        assert client.get("/auth/me").status_code == 401
        client.cookies.set(COOKIE_NAME, "invalid")
        assert client.get("/auth/me").status_code == 401


def test_auth_mutations_reject_untrusted_origin(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        response = client.post("/auth/register", json=VALID_USER, headers={"Origin": "https://attacker.test"})

    assert response.status_code == 403


def test_candidate_dashboard_and_setup_require_candidate_role(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)
        client.post("/auth/login", json=VALID_USER, headers=ORIGIN_HEADERS)

        dashboard = client.get("/candidate/dashboard")
        setup = client.get("/candidate/interview/setup")
        recruiter_dashboard = client.get("/recruiter/dashboard")
        recruiter_setup = client.get("/recruiter/interviews/new")

    assert dashboard.status_code == 200
    assert dashboard.json()["user"]["role"] == "CANDIDATE"
    assert dashboard.json()["previousAttempts"] == []
    assert dashboard.json()["performance"]["overallScore"] is None
    assert setup.status_code == 200
    assert "next feature" in setup.json()["message"]
    assert recruiter_dashboard.status_code == 403
    assert recruiter_setup.status_code == 403


def test_recruiter_role_is_database_backed_and_candidate_pages_are_forbidden(monkeypatch, tmp_path):
    with make_client(monkeypatch, tmp_path) as client:
        client.post("/auth/register", json=VALID_USER, headers=ORIGIN_HEADERS)
        candidate_login = client.post("/auth/login", json=VALID_USER, headers=ORIGIN_HEADERS)
        before_promotion = client.get("/candidate/dashboard")
        connection = sqlite3.connect(tmp_path / "auth.sqlite3")
        connection.execute(
            "UPDATE users SET role = 'RECRUITER' WHERE email = ?",
            (VALID_USER["email"],),
        )
        connection.commit()
        connection.close()
        current = client.get("/auth/me")
        candidate_dashboard = client.get("/candidate/dashboard")
        dashboard = client.get("/recruiter/dashboard")
        recruiter_setup = client.get("/recruiter/interviews/new")
        login = client.post("/auth/login", json=VALID_USER, headers=ORIGIN_HEADERS)

        candidate_setup = client.get("/candidate/interview/setup")

    assert candidate_login.json()["user"]["role"] == "CANDIDATE"
    assert before_promotion.status_code == 200
    assert current.json()["role"] == "RECRUITER"
    assert login.status_code == 200
    assert login.json()["user"]["role"] == "RECRUITER"
    assert dashboard.status_code == 200
    assert dashboard.json()["statistics"] == {
        "totalInterviews": 0,
        "candidatesEvaluated": 0,
        "averageScore": None,
    }
    assert dashboard.json()["createdInterviews"] == []
    assert candidate_dashboard.status_code == 403
    assert candidate_setup.status_code == 403
    assert recruiter_setup.status_code == 200


def test_existing_database_users_are_migrated_to_candidate_role(monkeypatch, tmp_path):
    database_path = tmp_path / "legacy.sqlite3"
    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL COLLATE NOCASE UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        INSERT INTO users (name, email, password_hash, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        ("Legacy Candidate", "legacy@example.com", "existing-hash", "2026-01-01", "2026-01-01"),
    )
    connection.commit()
    connection.close()

    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    from src.auth.database import initialize_database

    initialize_database()

    connection = sqlite3.connect(database_path)
    role = connection.execute("SELECT role FROM users WHERE email = ?", ("legacy@example.com",)).fetchone()[0]
    connection.close()
    assert role == "CANDIDATE"


def test_operator_role_command_updates_existing_account(monkeypatch, tmp_path):
    database_path = tmp_path / "role-command.sqlite3"
    monkeypatch.setenv("DATABASE_PATH", str(database_path))
    from src.auth.database import connect_database, initialize_database
    from scripts.set_user_role import main

    initialize_database()
    connection = connect_database()
    with connection:
        connection.execute(
            """
            INSERT INTO users (name, email, role, password_hash, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            ("Test Recruiter", "operator@example.com", "CANDIDATE", "hash", "2026-01-01", "2026-01-01"),
        )
    connection.close()

    monkeypatch.setattr(
        sys,
        "argv",
        ["set_user_role.py", "operator@example.com", "RECRUITER"],
    )
    assert main() == 0

    connection = sqlite3.connect(database_path)
    role = connection.execute(
        "SELECT role FROM users WHERE email = ?",
        ("operator@example.com",),
    ).fetchone()[0]
    connection.close()
    assert role == "RECRUITER"
