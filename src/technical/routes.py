from __future__ import annotations

import json
import random
import sqlite3
import time
import uuid
from datetime import datetime, timezone
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.auth.authorization import require_role
from src.auth.database import get_database
from src.auth.models import User, UserRole
from src.evaluator import AnswerEvaluator
from src.models import Question
from src.question_banks import TECHNICAL_QUESTIONS
from src.technical.adaptive import select_next_technical_question

router = APIRouter(prefix="/candidate/practice/technical", tags=["candidate technical interview"])
evaluator = AnswerEvaluator()


class TechnicalSessionCreateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    target_role: str = Field(alias="targetRole", min_length=2, max_length=100)
    experience_level: str = Field(alias="experienceLevel")
    topic: str | None = None
    total_questions: int = Field(default=5, alias="totalQuestions", ge=1, le=10)


class TechnicalQuestionResponse(BaseModel):
    id: str
    question: str
    topic: str
    category: str
    difficulty: str
    source: str
    license: str
    options: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)


class TechnicalSessionResponse(BaseModel):
    id: str
    status: str
    target_role: str = Field(serialization_alias="targetRole")
    experience_level: str = Field(serialization_alias="experienceLevel")
    topic: str
    total_questions: int = Field(serialization_alias="totalQuestions")
    current_index: int = Field(serialization_alias="currentIndex")
    question: TechnicalQuestionResponse | None

    model_config = ConfigDict(populate_by_name=True)


class TechnicalAnswerRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    answer: str
    selected_answer: int | None = Field(default=None, alias="selectedAnswer")


class TechnicalEvaluationResponse(BaseModel):
    question_id: str = Field(serialization_alias="questionId")
    score: int
    method: str
    correctness: str
    strengths: list[str]
    missing_concepts: list[str] = Field(serialization_alias="missingConcepts")
    suggestions: list[str]
    ideal_answer: str = Field(serialization_alias="idealAnswer")
    next_question: TechnicalQuestionResponse | None = Field(serialization_alias="nextQuestion")

    model_config = ConfigDict(populate_by_name=True)


class TechnicalResultResponse(BaseModel):
    session_id: str = Field(serialization_alias="sessionId")
    target_role: str = Field(serialization_alias="targetRole")
    experience_level: str = Field(serialization_alias="experienceLevel")
    topic: str
    total_questions: int = Field(serialization_alias="totalQuestions")
    answered: int
    average_score: float = Field(serialization_alias="averageScore")
    topic_performance: dict[str, float] = Field(serialization_alias="topicPerformance")
    difficulty_progression: list[str] = Field(serialization_alias="difficultyProgression")
    answers: list[dict[str, Any]]
    recommendation: str

    model_config = ConfigDict(populate_by_name=True)


def _question_response(q: dict[str, Any]) -> TechnicalQuestionResponse:
    return TechnicalQuestionResponse(
        id=q["id"],
        question=q["question"],
        topic=q["topic"],
        category=q["category"],
        difficulty=q["difficulty"],
        source=q["source"],
        license=q["license"],
        options=q.get("_options"),
    )


def _load_session(connection, session_id, user_id):
    row = connection.execute(
        "SELECT * FROM technical_interview_sessions WHERE id = ? AND user_id = ?",
        (session_id, user_id),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Session not found.")
    return row


def _ensure_options(question, bank):
    if question.get("_options"):
        return
    # Try LLM-generated distractors first.
    try:
        from src.rounds.routes import _llm_distractors, _truncate_option
        distractors = _llm_distractors(question)
        if distractors is not None:
            correct = _truncate_option(question["correct_answer"])
            options = distractors + [correct]
            rng = random.SystemRandom()
            rng.shuffle(options)
            options.append("I don't know")
            question["_options"] = options
            from src.rounds.routes import _TECHNICAL_OPTION_ANSWERS, _TECHNICAL_OPTIONS_CACHE
            _TECHNICAL_OPTIONS_CACHE[question["id"]] = options
            _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(correct)
            return
    except Exception:
        pass
    # Fallback: same-category distractors with word overlap.
    rng = random.SystemRandom()
    all_answers = [q["correct_answer"] for q in bank]
    correct = question["correct_answer"]
    same_topic = [q["correct_answer"] for q in bank if q["topic"] == question["topic"] and q["correct_answer"] != correct]
    candidates = [a for a in same_topic if __import__("src.rounds.routes", fromlist=["_word_overlap"])._word_overlap(correct, a) >= 0.15]
    if len(candidates) < 3:
        candidates = same_topic if len(same_topic) >= 3 else [a for a in all_answers if a != correct]
    if len(candidates) < 3:
        question["_options"] = None
        return
    distractors = rng.sample(candidates, min(3, len(candidates)))
    options = [_truncate_option(a) for a in distractors] + [_truncate_option(correct)]
    rng.shuffle(options)
    options.append("I don't know")
    question["_options"] = options
    from src.rounds.routes import _TECHNICAL_OPTION_ANSWERS, _TECHNICAL_OPTIONS_CACHE
    _TECHNICAL_OPTIONS_CACHE[question["id"]] = options
    _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(_truncate_option(correct))
@router.post("/sessions", response_model=TechnicalSessionResponse)
def create_session(
    payload: TechnicalSessionCreateRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> TechnicalSessionResponse:
    session_id = str(uuid.uuid4())
    now = int(time.time())
    topic = payload.topic or "General"
    bank = [q for q in TECHNICAL_QUESTIONS if topic.lower() in q["topic"].lower() or topic.lower() == "general"]
    if not bank:
        bank = TECHNICAL_QUESTIONS
    first = select_next_technical_question(bank, set(), [], payload.target_role, payload.experience_level)
    if first is None:
        raise HTTPException(status_code=400, detail="No questions available.")
    _ensure_options(first, TECHNICAL_QUESTIONS)
    with connection:
        connection.execute(
            """
            INSERT INTO technical_interview_sessions
            (id, user_id, target_role, experience_level, topic, status, total_questions, current_index, started_at)
            VALUES (?, ?, ?, ?, ?, 'IN_PROGRESS', ?, 0, ?)
            """,
            (session_id, user.id, payload.target_role, payload.experience_level, topic, payload.total_questions, now),
        )
        connection.execute(
            "INSERT INTO technical_session_questions (session_id, question_id, position, difficulty) VALUES (?, ?, 0, ?)",
            (session_id, first["id"], first["difficulty"]),
        )
    return TechnicalSessionResponse(
        id=session_id,
        status="IN_PROGRESS",
        target_role=payload.target_role,
        experience_level=payload.experience_level,
        topic=topic,
        total_questions=payload.total_questions,
        current_index=0,
        question=_question_response(first),
    )


@router.get("/sessions/{session_id}", response_model=TechnicalSessionResponse)
def get_session(
    session_id: str,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> TechnicalSessionResponse:
    session = _load_session(connection, session_id, user.id)
    current_index = session["current_index"]
    total = session["total_questions"]
    if current_index >= total:
        return TechnicalSessionResponse(
            id=session_id,
            status=session["status"],
            target_role=session["target_role"],
            experience_level=session["experience_level"],
            topic=session["topic"],
            total_questions=total,
            current_index=current_index,
            question=None,
        )
    row = connection.execute(
        "SELECT question_id FROM technical_session_questions WHERE session_id = ? AND position = ?",
        (session_id, current_index),
    ).fetchone()
    if row is None:
        return TechnicalSessionResponse(
            id=session_id,
            status=session["status"],
            target_role=session["target_role"],
            experience_level=session["experience_level"],
            topic=session["topic"],
            total_questions=total,
            current_index=current_index,
            question=None,
        )
    q = next((x for x in TECHNICAL_QUESTIONS if x["id"] == row["question_id"]), None)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found.")
    _ensure_options(q, TECHNICAL_QUESTIONS)
    return TechnicalSessionResponse(
        id=session_id,
        status=session["status"],
        target_role=session["target_role"],
        experience_level=session["experience_level"],
        topic=session["topic"],
        total_questions=total,
        current_index=current_index,
        question=_question_response(q),
    )
@router.post("/sessions/{session_id}/answers/{question_id}", response_model=TechnicalEvaluationResponse)
def submit_answer(
    session_id: str,
    question_id: str,
    payload: TechnicalAnswerRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> TechnicalEvaluationResponse:
    session = _load_session(connection, session_id, user.id)
    if session["status"] != "IN_PROGRESS":
        raise HTTPException(status_code=409, detail="Session already completed.")
    q = next((x for x in TECHNICAL_QUESTIONS if x["id"] == question_id), None)
    if q is None:
        raise HTTPException(status_code=404, detail="Question not found.")

    if payload.selected_answer is not None:
        from src.rounds.routes import _TECHNICAL_OPTION_ANSWERS
        correct_index = _TECHNICAL_OPTION_ANSWERS.get(question_id)
        if correct_index is None:
            _ensure_options(q, TECHNICAL_QUESTIONS)
            correct_index = _TECHNICAL_OPTION_ANSWERS.get(question_id)
        is_correct = payload.selected_answer == correct_index
        score = 100 if is_correct else 0
        evaluation = None
    else:
        question_obj = Question(
            prompt=q["question"],
            topic=q["topic"],
            difficulty=q["difficulty"],
            key_concepts=[q["topic"]],
            ideal_answer=q["correct_answer"],
            source="Local question bank",
        )
        evaluation = evaluator.evaluate(question_obj, payload.answer)
        score = evaluation.score
        is_correct = score >= 60

    now = int(time.time())
    with connection:
        connection.execute(
            """
            INSERT INTO technical_session_answers
            (session_id, question_id, answer, score, method, correctness, strengths, missing_concepts, suggestions, ideal_answer, answered_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                session_id,
                question_id,
                payload.answer if payload.selected_answer is None else f"Option {payload.selected_answer}",
                score,
                "Multiple-choice" if payload.selected_answer is not None else (evaluation.method if evaluation else "Rule-based fallback"),
                "Correct" if is_correct else "Incorrect",
                json.dumps([] if payload.selected_answer is not None else (evaluation.strengths if evaluation else [])),
                json.dumps([] if payload.selected_answer is not None else (evaluation.missing_concepts if evaluation else [])),
                json.dumps([] if payload.selected_answer is not None else (evaluation.suggestions if evaluation else [])),
                q["correct_answer"],
                now,
            ),
        )
        current_index = session["current_index"] + 1
        connection.execute(
            "UPDATE technical_interview_sessions SET current_index = ? WHERE id = ?",
            (current_index, session_id),
        )

    used_ids = {r["question_id"] for r in connection.execute(
        "SELECT question_id FROM technical_session_questions WHERE session_id = ?", (session_id,)
    ).fetchall()}
    used_ids.add(question_id)
    history_rows = connection.execute(
        "SELECT question_id, score FROM technical_session_answers WHERE session_id = ?", (session_id,)
    ).fetchall()
    history = []
    for hr in history_rows:
        hq = next((x for x in TECHNICAL_QUESTIONS if x["id"] == hr["question_id"]), None)
        if hq:
            history.append({"question_id": hr["question_id"], "topic": hq["topic"], "difficulty": hq["difficulty"], "score": hr["score"]})
    bank = TECHNICAL_QUESTIONS
    target_role = session["target_role"]
    experience = session["experience_level"]
    next_response = None
    if current_index < session["total_questions"]:
        next_q = select_next_technical_question(bank, used_ids, history, target_role, experience)
        if next_q is not None:
            _ensure_options(next_q, TECHNICAL_QUESTIONS)
            connection.execute(
                "INSERT INTO technical_session_questions (session_id, question_id, position, difficulty) VALUES (?, ?, ?, ?)",
                (session_id, next_q["id"], current_index, next_q["difficulty"]),
            )
            connection.commit()
            next_response = _question_response(next_q)

    strengths = [] if payload.selected_answer is not None else (evaluation.strengths if evaluation else [])
    missing = [] if payload.selected_answer is not None else (evaluation.missing_concepts if evaluation else [])
    suggestions = [] if payload.selected_answer is not None else (evaluation.suggestions if evaluation else [])
    ideal = q["correct_answer"]
    method = "Multiple-choice" if payload.selected_answer is not None else (evaluation.method if evaluation else "Rule-based fallback")
    correctness = "Correct" if is_correct else "Incorrect"

    return TechnicalEvaluationResponse(
        question_id=question_id,
        score=score,
        method=method,
        correctness=correctness,
        strengths=strengths,
        missing_concepts=missing,
        suggestions=suggestions,
        ideal_answer=ideal,
        next_question=next_response,
    )
@router.post("/sessions/{session_id}/submit", response_model=TechnicalResultResponse)
def submit_session(
    session_id: str,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> TechnicalResultResponse:
    session = _load_session(connection, session_id, user.id)
    if session["status"] == "IN_PROGRESS":
        now = int(time.time())
        connection.execute(
            "UPDATE technical_interview_sessions SET status = 'COMPLETED', completed_at = ? WHERE id = ?",
            (now, session_id),
        )
        connection.commit()
        session = _load_session(connection, session_id, user.id)
    return _result(connection, session)


@router.get("/sessions/{session_id}/result", response_model=TechnicalResultResponse)
def get_result(
    session_id: str,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
) -> TechnicalResultResponse:
    session = _load_session(connection, session_id, user.id)
    if session["status"] == "IN_PROGRESS":
        answers = connection.execute(
            "SELECT COUNT(*) FROM technical_session_answers WHERE session_id = ?", (session_id,)
        ).fetchone()[0]
        if answers >= session["total_questions"]:
            now = int(time.time())
            connection.execute(
                "UPDATE technical_interview_sessions SET status = 'COMPLETED', completed_at = ? WHERE id = ?",
                (now, session_id),
            )
            connection.commit()
            session = _load_session(connection, session_id, user.id)
    return _result(connection, session)


def _result(connection, session):
    session_id = session["id"]
    answers = connection.execute(
        "SELECT * FROM technical_session_answers WHERE session_id = ? ORDER BY answered_at",
        (session_id,),
    ).fetchall()
    scores = [r["score"] for r in answers]
    avg = sum(scores) / len(scores) if scores else 0.0
    topic_perf: dict[str, list[int]] = {}
    difficulty_progression = []
    answer_list = []
    for r in answers:
        q = next((x for x in TECHNICAL_QUESTIONS if x["id"] == r["question_id"]), None)
        topic = q["topic"] if q else "Unknown"
        topic_perf.setdefault(topic, []).append(r["score"])
        difficulty_progression.append(q["difficulty"] if q else "Medium")
        answer_list.append({
            "question_id": r["question_id"],
            "question": q["question"] if q else "",
            "answer": r["answer"],
            "score": r["score"],
            "method": r["method"],
            "correctness": r["correctness"],
            "ideal_answer": r["ideal_answer"],
            "strengths": json.loads(r["strengths"]),
            "missing_concepts": json.loads(r["missing_concepts"]),
            "suggestions": json.loads(r["suggestions"]),
        })
    topic_performance = {t: (sum(s) / len(s)) for t, s in topic_perf.items()}
    if avg >= 80:
        recommendation = "Strong performance. Move to harder topics and system design."
    elif avg >= 50:
        recommendation = "Good progress. Focus on weak topics and deeper follow-ups."
    else:
        recommendation = "Review fundamentals and practice core concepts."
    return TechnicalResultResponse(
        session_id=session_id,
        target_role=session["target_role"],
        experience_level=session["experience_level"],
        topic=session["topic"],
        total_questions=session["total_questions"],
        answered=len(answers),
        average_score=round(avg, 1),
        topic_performance=topic_performance,
        difficulty_progression=difficulty_progression,
        answers=answer_list,
        recommendation=recommendation,
    )


@router.get("/history")
def history(
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
    connection: Annotated[sqlite3.Connection, Depends(get_database)],
):
    rows = connection.execute(
        "SELECT * FROM technical_interview_sessions WHERE user_id = ? ORDER BY started_at DESC",
        (user.id,),
    ).fetchall()
    return [dict(row) for row in rows]