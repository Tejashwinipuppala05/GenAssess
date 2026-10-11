from __future__ import annotations

import json
import sqlite3
import time
import uuid
from collections import defaultdict
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.authorization import require_role
from src.auth.database import get_database
from src.auth.models import User, UserRole
from .schemas import (
    AptitudeAnswerReview,
    AptitudeAnswerUpdateRequest,
    AptitudeCategoryResult,
    AptitudeDifficultyResult,
    AptitudeHistoryItem,
    AptitudeQuestionResponse,
    AptitudeResultResponse,
    AptitudeSessionConfigResponse,
    AptitudeSessionCreateRequest,
    AptitudeSessionResponse,
    AptitudeTopicResult,
)
from .selection import CATEGORIES, load_selection_config, select_questions

router = APIRouter(prefix="/candidate/practice/aptitude", tags=["candidate aptitude practice"])


def _question_from_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "id": row["id"],
        "question": row["question"],
        "options": json.loads(row["options_json"]),
        "topic": row["topic"],
        "subtopic": row["subtopic"],
        "category": row["category"],
        "difficulty": row["difficulty"],
        "estimated_time_seconds": row["estimated_time_seconds"],
        "source_type": row["source_type"],
        "tags": json.loads(row["tags_json"]),
        "target_roles": json.loads(row["target_roles_json"]),
        "correct_answer": row["correct_answer"],
        "explanation": row["explanation"],
    }


def _load_active_questions(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM aptitude_questions WHERE active = 1 ORDER BY id"
    ).fetchall()
    return [_question_from_row(row) for row in rows]


def _load_candidate_history(connection: sqlite3.Connection, user_id: int) -> list[dict[str, Any]]:
    rows = connection.execute(
        """
        SELECT
            question.id AS question_id,
            question.topic,
            question.difficulty,
            answer.is_correct,
            session.started_at AS attempted_at
        FROM aptitude_session_questions AS session_question
        JOIN aptitude_practice_sessions AS session
            ON session.id = session_question.session_id
        JOIN aptitude_questions AS question
            ON question.id = session_question.question_id
        LEFT JOIN aptitude_practice_answers AS answer
            ON answer.session_id = session_question.session_id
            AND answer.question_id = session_question.question_id
        WHERE session.user_id = ?
        ORDER BY session.started_at DESC
        """,
        (user_id,),
    ).fetchall()
    return [dict(row) for row in rows]


def _owned_session(
    connection: sqlite3.Connection,
    user_id: int,
    session_id: str,
) -> sqlite3.Row:
    row = connection.execute(
        "SELECT * FROM aptitude_practice_sessions WHERE id = ? AND user_id = ?",
        (session_id, user_id),
    ).fetchone()
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Aptitude practice session was not found.",
        )
    return row


def _build_session_response(
    connection: sqlite3.Connection,
    session: sqlite3.Row,
    now: int,
) -> AptitudeSessionResponse:
    question_rows = connection.execute(
        """
        SELECT question.*, answer.selected_option, answer.marked_for_review
        FROM aptitude_session_questions AS session_question
        JOIN aptitude_questions AS question ON question.id = session_question.question_id
        LEFT JOIN aptitude_practice_answers AS answer
            ON answer.session_id = session_question.session_id
            AND answer.question_id = session_question.question_id
        WHERE session_question.session_id = ?
        ORDER BY session_question.ordinal
        """,
        (session["id"],),
    ).fetchall()
    questions = [
        AptitudeQuestionResponse(
            id=row["id"],
            question=row["question"],
            options=json.loads(row["options_json"]),
            topic=row["topic"],
            subtopic=row["subtopic"],
            category=row["category"],
            difficulty=row["difficulty"],
            estimated_time_seconds=row["estimated_time_seconds"],
            source_type=row["source_type"],
            tags=json.loads(row["tags_json"]),
            selected_answer=row["selected_option"],
            marked_for_review=bool(row["marked_for_review"] or 0),
        )
        for row in question_rows
    ]
    return AptitudeSessionResponse(
        id=session["id"],
        status=session["status"],
        target_role=session["target_role"],
        company_type=session["company_type"],
        experience_level=session["experience_level"],
        started_at=session["started_at"],
        expires_at=session["expires_at"],
        server_time=now,
        duration_seconds=session["duration_seconds"],
        total_questions=session["total_questions"],
        questions=questions,
    )


def _percentage(correct: int, total: int) -> float:
    return round(correct * 100 / total, 1) if total else 0.0


def _finish_session(
    connection: sqlite3.Connection,
    session: sqlite3.Row,
    submitted_at: int,
) -> None:
    if session["status"] == "COMPLETED":
        return

    questions = connection.execute(
        """
        SELECT question.id, question.correct_answer
        FROM aptitude_session_questions AS session_question
        JOIN aptitude_questions AS question ON question.id = session_question.question_id
        WHERE session_question.session_id = ?
        ORDER BY session_question.ordinal
        """,
        (session["id"],),
    ).fetchall()
    correct_count = 0
    incorrect_count = 0
    unanswered_count = 0
    for question in questions:
        answer = connection.execute(
            """
            SELECT selected_option
            FROM aptitude_practice_answers
            WHERE session_id = ? AND question_id = ?
            """,
            (session["id"], question["id"]),
        ).fetchone()
        selected_option = answer["selected_option"] if answer is not None else None
        is_correct = None if selected_option is None else int(selected_option == question["correct_answer"])
        if is_correct is None:
            unanswered_count += 1
            connection.execute(
                """
                INSERT OR IGNORE INTO aptitude_practice_answers (
                    session_id, question_id, selected_option, marked_for_review, answered_at, is_correct
                )
                VALUES (?, ?, NULL, 0, NULL, NULL)
                """,
                (session["id"], question["id"]),
            )
        elif is_correct:
            correct_count += 1
            connection.execute(
                """
                UPDATE aptitude_practice_answers SET is_correct = ?
                WHERE session_id = ? AND question_id = ?
                """,
                (is_correct, session["id"], question["id"]),
            )
        else:
            incorrect_count += 1
            connection.execute(
                """
                UPDATE aptitude_practice_answers SET is_correct = ?
                WHERE session_id = ? AND question_id = ?
                """,
                (is_correct, session["id"], question["id"]),
            )

    elapsed_seconds = max(0, submitted_at - session["started_at"])
    time_taken = min(session["duration_seconds"], elapsed_seconds)
    accuracy = _percentage(correct_count, len(questions))
    connection.execute(
        """
        UPDATE aptitude_practice_sessions
        SET status = 'COMPLETED', submitted_at = ?, time_taken_seconds = ?,
            correct_answers = ?, incorrect_answers = ?, unanswered_questions = ?,
            score = ?, accuracy = ?
        WHERE id = ? AND user_id = ? AND status = 'IN_PROGRESS'
        """,
        (
            submitted_at,
            time_taken,
            correct_count,
            incorrect_count,
            unanswered_count,
            correct_count,
            accuracy,
            session["id"],
            session["user_id"],
        ),
    )
    connection.commit()


def _result_for_session(
    connection: sqlite3.Connection,
    session: sqlite3.Row,
) -> AptitudeResultResponse:
    if session["status"] != "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Submit the practice session before viewing its result.",
        )

    rows = connection.execute(
        """
        SELECT
            question.id, question.question, question.options_json, question.correct_answer,
            question.explanation, question.topic, question.subtopic, question.category,
            question.difficulty, answer.selected_option, answer.is_correct
        FROM aptitude_session_questions AS session_question
        JOIN aptitude_questions AS question ON question.id = session_question.question_id
        LEFT JOIN aptitude_practice_answers AS answer
            ON answer.session_id = session_question.session_id
            AND answer.question_id = session_question.question_id
        WHERE session_question.session_id = ?
        ORDER BY session_question.ordinal
        """,
        (session["id"],),
    ).fetchall()

    category_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    topic_counts: dict[tuple[str, str], list[int]] = defaultdict(lambda: [0, 0])
    difficulty_counts: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    answer_reviews: list[AptitudeAnswerReview] = []
    for row in rows:
        selected_option = row["selected_option"]
        is_correct = None if selected_option is None else bool(row["is_correct"])
        category_counts[row["category"]][0] += 1
        topic_counts[(row["topic"], row["category"])][0] += 1
        difficulty_counts[row["difficulty"]][0] += 1
        if is_correct:
            category_counts[row["category"]][1] += 1
            topic_counts[(row["topic"], row["category"])][1] += 1
            difficulty_counts[row["difficulty"]][1] += 1
        answer_reviews.append(
            AptitudeAnswerReview(
                question_id=row["id"],
                question=row["question"],
                options=json.loads(row["options_json"]),
                selected_answer=selected_option,
                correct_answer=row["correct_answer"],
                is_correct=is_correct,
                explanation=row["explanation"],
                topic=row["topic"],
                subtopic=row["subtopic"],
                category=row["category"],
                difficulty=row["difficulty"],
            )
        )

    category_results = [
        AptitudeCategoryResult(
            category=category,
            total=total,
            correct=correct,
            incorrect=sum(
                1
                for row in rows
                if row["category"] == category
                and row["selected_option"] is not None
                and not row["is_correct"]
            ),
            unanswered=sum(
                1
                for row in rows
                if row["category"] == category and row["selected_option"] is None
            ),
            accuracy=_percentage(correct, total),
        )
        for category, (total, correct) in category_counts.items()
    ]
    topic_results = [
        AptitudeTopicResult(
            topic=topic,
            category=category,
            total=total,
            correct=correct,
            incorrect=sum(
                1
                for row in rows
                if row["topic"] == topic
                and row["category"] == category
                and row["selected_option"] is not None
                and not row["is_correct"]
            ),
            unanswered=sum(
                1
                for row in rows
                if row["topic"] == topic
                and row["category"] == category
                and row["selected_option"] is None
            ),
            accuracy=_percentage(correct, total),
        )
        for (topic, category), (total, correct) in topic_counts.items()
    ]
    difficulty_results = [
        AptitudeDifficultyResult(
            difficulty=difficulty,
            total=total,
            correct=correct,
            incorrect=sum(
                1
                for row in rows
                if row["difficulty"] == difficulty
                and row["selected_option"] is not None
                and not row["is_correct"]
            ),
            unanswered=sum(
                1
                for row in rows
                if row["difficulty"] == difficulty and row["selected_option"] is None
            ),
            accuracy=_percentage(correct, total),
        )
        for difficulty, (total, correct) in difficulty_counts.items()
    ]
    weak_topics = sorted(
        result.topic for result in topic_results if result.accuracy < 60
    )
    strong_topics = sorted(
        result.topic for result in topic_results if result.accuracy >= 80 and result.correct > 0
    )
    recommendation = (
        "Practice " + ", ".join(weak_topics[:3]) + " before your next aptitude test."
        if weak_topics
        else "Good progress. Keep practicing mixed-difficulty questions before your next aptitude test."
    )
    return AptitudeResultResponse(
        session_id=session["id"],
        target_role=session["target_role"],
        company_type=session["company_type"],
        experience_level=session["experience_level"],
        total_questions=session["total_questions"],
        correct_answers=session["correct_answers"],
        incorrect_answers=session["incorrect_answers"],
        unanswered_questions=session["unanswered_questions"],
        score=int(session["score"]),
        accuracy=session["accuracy"],
        time_taken_seconds=session["time_taken_seconds"],
        duration_seconds=session["duration_seconds"],
        completed_at=session["submitted_at"],
        category_performance=category_results,
        topic_performance=topic_results,
        difficulty_performance=difficulty_results,
        strong_topics=strong_topics,
        weak_topics=weak_topics,
        recommendation=recommendation,
        answers=answer_reviews,
    )


@router.get("/config", response_model=AptitudeSessionConfigResponse)
def get_session_config(
    _: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> AptitudeSessionConfigResponse:
    try:
        config = load_selection_config()
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The aptitude session pattern is misconfigured.",
        ) from exc
    estimates = connection.execute(
        """
        SELECT category, AVG(estimated_time_seconds) AS average_seconds
        FROM aptitude_questions
        WHERE active = 1
        GROUP BY category
        """
    ).fetchall()
    average_by_category = {row["category"]: row["average_seconds"] for row in estimates}
    estimated_duration = sum(
        round(average_by_category.get(category, 60) * count)
        for category, count in config.category_counts.items()
    )
    return AptitudeSessionConfigResponse(
        question_count=config.question_count,
        estimated_duration_seconds=estimated_duration,
        category_counts=config.category_counts,
        difficulty_distribution=config.difficulty_distribution,
        categories=tuple(category for category in CATEGORIES if category in config.category_counts),
    )


@router.post("/sessions", response_model=AptitudeSessionResponse, status_code=status.HTTP_201_CREATED)
def create_session(
    payload: AptitudeSessionCreateRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> AptitudeSessionResponse:
    try:
        config = load_selection_config()
        history = _load_candidate_history(connection, user.id)
        selected = select_questions(
            _load_active_questions(connection),
            config,
            payload.target_role,
            payload.experience_level,
            history,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="The aptitude question bank or session pattern cannot support a complete test.",
        ) from exc

    if len(selected) != config.question_count:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="There are not enough active aptitude questions for this session.",
        )
    started_at = int(time.time())
    duration_seconds = sum(question["estimated_time_seconds"] for question in selected)
    session_id = str(uuid.uuid4())
    connection.execute(
        """
        INSERT INTO aptitude_practice_sessions (
            id, user_id, target_role, company_type, experience_level, status,
            started_at, expires_at, submitted_at, total_questions, duration_seconds
        )
        VALUES (?, ?, ?, ?, ?, 'IN_PROGRESS', ?, ?, NULL, ?, ?)
        """,
        (
            session_id,
            user.id,
            payload.target_role,
            payload.company_type,
            payload.experience_level,
            started_at,
            started_at + duration_seconds,
            len(selected),
            duration_seconds,
        ),
    )
    connection.executemany(
        """
        INSERT INTO aptitude_session_questions (session_id, question_id, ordinal)
        VALUES (?, ?, ?)
        """,
        [(session_id, question["id"], ordinal) for ordinal, question in enumerate(selected)],
    )
    connection.commit()
    session = _owned_session(connection, user.id, session_id)
    return _build_session_response(connection, session, int(time.time()))


@router.get("/sessions", response_model=list[AptitudeHistoryItem])
def list_sessions(
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> list[AptitudeHistoryItem]:
    now = int(time.time())
    expired_sessions = connection.execute(
        """
        SELECT * FROM aptitude_practice_sessions
        WHERE user_id = ? AND status = 'IN_PROGRESS' AND expires_at <= ?
        """,
        (user.id, now),
    ).fetchall()
    for session in expired_sessions:
        _finish_session(connection, session, session["expires_at"])
    rows = connection.execute(
        """
        SELECT id, target_role, company_type, experience_level, status, started_at,
               total_questions, correct_answers, accuracy, time_taken_seconds
        FROM aptitude_practice_sessions
        WHERE user_id = ?
        ORDER BY started_at DESC
        LIMIT 50
        """,
        (user.id,),
    ).fetchall()
    return [
        AptitudeHistoryItem(
            session_id=row["id"],
            target_role=row["target_role"],
            company_type=row["company_type"],
            experience_level=row["experience_level"],
            status=row["status"],
            started_at=row["started_at"],
            total_questions=row["total_questions"],
            correct_answers=row["correct_answers"],
            accuracy=row["accuracy"],
            time_taken_seconds=row["time_taken_seconds"],
        )
        for row in rows
    ]


@router.get("/sessions/{session_id}", response_model=AptitudeSessionResponse)
def get_session(
    session_id: str,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> AptitudeSessionResponse:
    session = _owned_session(connection, user.id, session_id)
    now = int(time.time())
    if session["status"] == "IN_PROGRESS" and now >= session["expires_at"]:
        _finish_session(connection, session, session["expires_at"])
        session = _owned_session(connection, user.id, session_id)
    return _build_session_response(connection, session, now)


@router.put("/sessions/{session_id}/answers/{question_id}")
def save_answer(
    session_id: str,
    question_id: str,
    payload: AptitudeAnswerUpdateRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> dict[str, bool]:
    session = _owned_session(connection, user.id, session_id)
    now = int(time.time())
    if session["status"] == "COMPLETED":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This aptitude practice session has already been submitted.",
        )
    if now >= session["expires_at"]:
        _finish_session(connection, session, session["expires_at"])
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="The session timer expired and the test was submitted automatically.",
        )
    belongs = connection.execute(
        """
        SELECT 1 FROM aptitude_session_questions
        WHERE session_id = ? AND question_id = ?
        """,
        (session_id, question_id),
    ).fetchone()
    if belongs is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="The question does not belong to this practice session.",
        )

    answered_at = now if payload.selected_answer is not None else None
    connection.execute(
        """
        INSERT INTO aptitude_practice_answers (
            session_id, question_id, selected_option, marked_for_review, answered_at, is_correct
        )
        VALUES (?, ?, ?, ?, ?, NULL)
        ON CONFLICT(session_id, question_id) DO UPDATE SET
            selected_option = excluded.selected_option,
            marked_for_review = excluded.marked_for_review,
            answered_at = excluded.answered_at
        """,
        (
            session_id,
            question_id,
            payload.selected_answer,
            int(payload.marked_for_review),
            answered_at,
        ),
    )
    connection.commit()
    return {"saved": True}


@router.post("/sessions/{session_id}/submit", response_model=AptitudeResultResponse)
def submit_session(
    session_id: str,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> AptitudeResultResponse:
    session = _owned_session(connection, user.id, session_id)
    if session["status"] == "IN_PROGRESS":
        submitted_at = min(int(time.time()), session["expires_at"])
        _finish_session(connection, session, submitted_at)
        session = _owned_session(connection, user.id, session_id)
    return _result_for_session(connection, session)


@router.get("/sessions/{session_id}/result", response_model=AptitudeResultResponse)
def get_result(
    session_id: str,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> AptitudeResultResponse:
    session = _owned_session(connection, user.id, session_id)
    if session["status"] == "IN_PROGRESS" and int(time.time()) >= session["expires_at"]:
        _finish_session(connection, session, session["expires_at"])
        session = _owned_session(connection, user.id, session_id)
    return _result_for_session(connection, session)
