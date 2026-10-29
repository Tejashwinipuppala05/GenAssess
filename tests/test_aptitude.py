from __future__ import annotations

import json
import sqlite3
import time

import pytest
from fastapi.testclient import TestClient

from auth_api import app
from src.aptitude.bank import QUESTION_BANK
from src.auth.database import initialize_database
from src.aptitude.selection import (
    DEFAULT_DIFFICULTY_DISTRIBUTION,
    SelectionConfig,
    adapted_difficulty_distribution,
    select_questions,
    topic_selection_weights,
)

FRONTEND_ORIGIN = "http://localhost:3000"
ORIGIN_HEADERS = {"Origin": FRONTEND_ORIGIN}
USER = {
    "name": "Practice Candidate",
    "email": "practice@example.com",
    "password": "correct horse battery staple",
}


@pytest.fixture
def candidate_client(monkeypatch, tmp_path) -> TestClient:
    monkeypatch.setenv("JWT_SECRET", "test-secret-that-is-at-least-32-bytes-long")
    monkeypatch.setenv("DATABASE_PATH", str(tmp_path / "aptitude.sqlite3"))
    monkeypatch.setenv("FRONTEND_ORIGIN", FRONTEND_ORIGIN)
    monkeypatch.setenv("COOKIE_SECURE", "false")
    monkeypatch.delenv("APTITUDE_CATEGORY_COUNTS", raising=False)
    monkeypatch.delenv("APTITUDE_DIFFICULTY_DISTRIBUTION", raising=False)
    with TestClient(app) as client:
        registered = client.post("/auth/register", json=USER, headers=ORIGIN_HEADERS)
        assert registered.status_code == 201
        logged_in = client.post("/auth/login", json=USER, headers=ORIGIN_HEADERS)
        assert logged_in.status_code == 200
        yield client


def start_session(client: TestClient, role: str = "Software Engineer") -> dict:
    response = client.post(
        "/candidate/practice/aptitude/sessions",
        json={"targetRole": role, "companyType": "Product company", "experienceLevel": "Fresher"},
        headers=ORIGIN_HEADERS,
    )
    assert response.status_code == 201, response.text
    return response.json()


def test_answer_save_preflight_allows_put(candidate_client):
    response = candidate_client.options(
        "/candidate/practice/aptitude/sessions/session/answers/question",
        headers={
            **ORIGIN_HEADERS,
            "Access-Control-Request-Method": "PUT",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == FRONTEND_ORIGIN
    assert "PUT" in response.headers["access-control-allow-methods"]


def test_question_bank_is_original_seeded_data_with_topic_and_difficulty_coverage(
    candidate_client,
    tmp_path,
):
    config = candidate_client.get("/candidate/practice/aptitude/config")
    assert config.status_code == 200
    assert config.json()["questionCount"] == 20
    assert config.json()["categoryCounts"] == {
        "Quantitative Aptitude": 8,
        "Logical Reasoning": 6,
        "Verbal Ability": 6,
    }
    assert config.json()["difficultyDistribution"] == {
        "Easy": 30,
        "Medium": 50,
        "Hard": 20,
    }

    connection = sqlite3.connect(tmp_path / "aptitude.sqlite3")
    bank_count, original_count, topic_count = connection.execute(
        """
        SELECT COUNT(*), SUM(source_type = 'Original GenAssess question'), COUNT(DISTINCT topic)
        FROM aptitude_questions
        """
    ).fetchone()
    connection.close()
    assert bank_count == len(QUESTION_BANK)
    assert original_count == 71
    assert topic_count >= 35


def test_question_bank_correct_answer_indices_match_their_options():
    for question in QUESTION_BANK:
        assert 0 <= question["correct_answer"] < len(question["options"])
    mixture_question = next(question for question in QUESTION_BANK if question["id"] == "qa-mix-02")
    assert mixture_question["options"][mixture_question["correct_answer"]] == "3:1"


def test_bank_seeding_updates_unused_questions_but_preserves_session_history(candidate_client, tmp_path):
    session = start_session(candidate_client)
    selected_ids = {question["id"] for question in session["questions"]}
    unused_question = next(question for question in QUESTION_BANK if question["id"] not in selected_ids)
    connection = sqlite3.connect(tmp_path / "aptitude.sqlite3")
    connection.execute(
        "UPDATE aptitude_questions SET question = 'Old wording' WHERE id IN (?, ?)",
        (next(iter(selected_ids)), unused_question["id"]),
    )
    connection.commit()
    connection.close()

    initialize_database()

    connection = sqlite3.connect(tmp_path / "aptitude.sqlite3")
    bank_questions = dict(
        connection.execute(
            "SELECT id, question FROM aptitude_questions WHERE id IN (?, ?)",
            (next(iter(selected_ids)), unused_question["id"]),
        ).fetchall()
    )
    connection.close()
    assert bank_questions[next(iter(selected_ids))] == "Old wording"
    assert bank_questions[unused_question["id"]] == unused_question["question"]


def test_session_selection_is_random_balanced_and_avoids_repeats(candidate_client):
    first = start_session(candidate_client)
    second = start_session(candidate_client)
    first_questions = first["questions"]
    second_questions = second["questions"]

    assert len(first_questions) == 20
    assert len({question["id"] for question in first_questions}) == 20
    assert {question["id"] for question in first_questions}.isdisjoint(
        question["id"] for question in second_questions
    )
    assert not any("correctAnswer" in question for question in first_questions)
    assert first["expiresAt"] - first["startedAt"] == first["durationSeconds"]

    category_counts: dict[str, int] = {}
    difficulty_counts: dict[str, int] = {}
    for question in first_questions:
        category_counts[question["category"]] = category_counts.get(question["category"], 0) + 1
        difficulty_counts[question["difficulty"]] = difficulty_counts.get(question["difficulty"], 0) + 1
    assert category_counts == {
        "Quantitative Aptitude": 8,
        "Logical Reasoning": 6,
        "Verbal Ability": 6,
    }
    assert difficulty_counts == {"Easy": 6, "Medium": 10, "Hard": 4}


def test_answers_are_saved_and_results_include_scoring_and_topic_analysis(candidate_client):
    session = start_session(candidate_client)
    answer_map = {question["id"]: question for question in QUESTION_BANK}
    questions = session["questions"]
    first, second = questions[:2]
    correct_option = answer_map[first["id"]]["correct_answer"]
    wrong_option = (answer_map[second["id"]]["correct_answer"] + 1) % 4

    for question, selected, mark in ((first, correct_option, True), (second, wrong_option, False)):
        response = candidate_client.put(
            f"/candidate/practice/aptitude/sessions/{session['id']}/answers/{question['id']}",
            json={"selectedAnswer": selected, "markedForReview": mark},
            headers=ORIGIN_HEADERS,
        )
        assert response.status_code == 200

    resumed = candidate_client.get(f"/candidate/practice/aptitude/sessions/{session['id']}")
    assert resumed.status_code == 200
    assert resumed.json()["questions"][0]["selectedAnswer"] == correct_option
    assert resumed.json()["questions"][0]["markedForReview"] is True

    submitted = candidate_client.post(
        f"/candidate/practice/aptitude/sessions/{session['id']}/submit",
        headers=ORIGIN_HEADERS,
    )
    assert submitted.status_code == 200
    result = submitted.json()
    assert result["totalQuestions"] == 20
    assert result["correctAnswers"] == 1
    assert result["incorrectAnswers"] == 1
    assert result["unansweredQuestions"] == 18
    assert result["score"] == 1
    assert result["accuracy"] == 5.0
    assert result["timeTakenSeconds"] <= result["durationSeconds"]
    assert sum(item["total"] for item in result["categoryPerformance"]) == 20
    assert sum(item["total"] for item in result["topicPerformance"]) == 20
    assert sum(item["total"] for item in result["difficultyPerformance"]) == 20
    assert all("correctAnswer" in answer and "explanation" in answer for answer in result["answers"])
    assert result["recommendation"].startswith("Practice ")

    history = candidate_client.get("/candidate/practice/aptitude/sessions")
    assert history.status_code == 200
    assert history.json()[0]["sessionId"] == session["id"]
    assert history.json()[0]["correctAnswers"] == 1


def test_backend_timer_auto_submits_and_rejects_late_answer(candidate_client, tmp_path):
    session = start_session(candidate_client)
    connection = sqlite3.connect(tmp_path / "aptitude.sqlite3")
    connection.execute(
        "UPDATE aptitude_practice_sessions SET expires_at = ? WHERE id = ?",
        (int(time.time()) - 1, session["id"]),
    )
    connection.commit()
    connection.close()

    expired = candidate_client.get(f"/candidate/practice/aptitude/sessions/{session['id']}")
    result = candidate_client.get(
        f"/candidate/practice/aptitude/sessions/{session['id']}/result"
    )
    late_answer = candidate_client.put(
        f"/candidate/practice/aptitude/sessions/{session['id']}/answers/{session['questions'][0]['id']}",
        json={"selectedAnswer": 0},
        headers=ORIGIN_HEADERS,
    )

    assert expired.status_code == 200
    assert expired.json()["status"] == "COMPLETED"
    assert result.status_code == 200
    assert result.json()["unansweredQuestions"] == 20
    assert late_answer.status_code == 409


def test_session_is_candidate_only_and_private_to_its_owner(monkeypatch, candidate_client):
    session = start_session(candidate_client)
    candidate_client.post("/auth/logout", headers=ORIGIN_HEADERS)
    recruiter = {
        "name": "Recruiter",
        "email": "aptitude-recruiter@example.com",
        "password": "correct horse battery staple",
        "role": "RECRUITER",
    }
    candidate_client.post("/auth/register", json=recruiter, headers=ORIGIN_HEADERS)
    candidate_client.post("/auth/login", json=recruiter, headers=ORIGIN_HEADERS)

    forbidden = candidate_client.get(f"/candidate/practice/aptitude/sessions/{session['id']}")
    recruiter_create = candidate_client.post(
        "/candidate/practice/aptitude/sessions",
        json={"targetRole": "Analyst", "experienceLevel": "Fresher"},
        headers=ORIGIN_HEADERS,
    )
    assert forbidden.status_code == 403
    assert recruiter_create.status_code == 403


def test_adaptive_policy_shifts_difficulty_and_boosts_weak_topics():
    low_history = [{"is_correct": False} for _ in range(10)]
    high_history = [{"is_correct": True} for _ in range(10)]
    low_distribution = adapted_difficulty_distribution(
        DEFAULT_DIFFICULTY_DISTRIBUTION,
        low_history,
        "Fresher",
    )
    high_distribution = adapted_difficulty_distribution(
        DEFAULT_DIFFICULTY_DISTRIBUTION,
        high_history,
        "Fresher",
    )
    experienced_distribution = adapted_difficulty_distribution(
        DEFAULT_DIFFICULTY_DISTRIBUTION,
        [],
        "Experienced",
    )
    topic_weights = topic_selection_weights(
        [
            {"topic": "Percentages", "is_correct": False},
            {"topic": "Percentages", "is_correct": False},
            {"topic": "Number Series", "is_correct": True},
        ]
    )

    assert low_distribution == {"Easy": 40, "Medium": 50, "Hard": 10}
    assert high_distribution == {"Easy": 20, "Medium": 50, "Hard": 30}
    assert experienced_distribution == {"Easy": 20, "Medium": 50, "Hard": 30}
    assert topic_weights["Percentages"] > topic_weights["Number Series"]


def test_selector_prefers_unseen_and_respects_configured_categories_and_difficulty():
    config = SelectionConfig(
        category_counts={"Quantitative Aptitude": 4},
        difficulty_distribution={"Easy": 25, "Medium": 50, "Hard": 25},
    )
    history = [
        {
            "question_id": question["id"],
            "topic": question["topic"],
            "difficulty": question["difficulty"],
            "is_correct": None,
            "attempted_at": index,
        }
        for index, question in enumerate(QUESTION_BANK[:4])
        if question["category"] == "Quantitative Aptitude"
    ]
    selected = select_questions(
        QUESTION_BANK,
        config,
        "Data Analyst",
        "Fresher",
        history,
    )
    assert len(selected) == 4
    assert len({question["id"] for question in selected}) == 4
    assert all(question["id"] not in {attempt["question_id"] for attempt in history} for question in selected)


def test_invalid_environment_pattern_is_reported(monkeypatch, candidate_client):
    monkeypatch.setenv("APTITUDE_CATEGORY_COUNTS", json.dumps({"Unknown": 20}))
    response = candidate_client.post(
        "/candidate/practice/aptitude/sessions",
        json={"targetRole": "Analyst", "experienceLevel": "Fresher"},
        headers=ORIGIN_HEADERS,
    )
    assert response.status_code == 503
