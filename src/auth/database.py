from __future__ import annotations

import os
import json
import sqlite3
from collections.abc import Generator
from pathlib import Path


def database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", "data/genassess.db")).expanduser()


def connect_database() -> sqlite3.Connection:
    path = database_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(path, timeout=10, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def get_database() -> Generator[sqlite3.Connection, None, None]:
    connection = connect_database()
    try:
        yield connection
    finally:
        connection.close()


def initialize_database() -> None:
    connection = connect_database()
    try:
        with connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    email TEXT COLLATE NOCASE UNIQUE,
                    phone TEXT UNIQUE,
                    supabase_user_id TEXT UNIQUE,
                    role TEXT NOT NULL DEFAULT 'CANDIDATE'
                        CHECK (role IN ('CANDIDATE', 'RECRUITER')),
                    password_hash TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS user_sessions (
                    token_id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    expires_at INTEGER NOT NULL,
                    revoked_at INTEGER,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS user_sessions_user_id_idx
                    ON user_sessions(user_id);

                CREATE TABLE IF NOT EXISTS company_verifications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
                    company_name TEXT NOT NULL,
                    identifier_type TEXT NOT NULL CHECK (identifier_type IN ('CIN', 'GSTIN')),
                    identifier TEXT NOT NULL,
                    website_url TEXT NOT NULL,
                    linkedin_url TEXT NOT NULL,
                    registry_status TEXT NOT NULL,
                    registry_company_name TEXT,
                    status TEXT NOT NULL CHECK (
                        status IN ('PENDING_REVIEW', 'VERIFIED', 'REJECTED', 'REGISTRY_FAILED')
                    ),
                    reviewer_note TEXT,
                    reviewed_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS job_posts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recruiter_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    location TEXT NOT NULL,
                    work_arrangement TEXT NOT NULL CHECK (
                        work_arrangement IN ('REMOTE', 'HYBRID', 'ONSITE')
                    ),
                    created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS job_posts_recruiter_id_idx
                    ON job_posts(recruiter_id);

                CREATE TABLE IF NOT EXISTS aptitude_questions (
                    id TEXT PRIMARY KEY,
                    question TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    correct_answer INTEGER NOT NULL CHECK (correct_answer BETWEEN 0 AND 3),
                    explanation TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    subtopic TEXT NOT NULL,
                    category TEXT NOT NULL,
                    difficulty TEXT NOT NULL CHECK (difficulty IN ('Easy', 'Medium', 'Hard')),
                    estimated_time_seconds INTEGER NOT NULL CHECK (estimated_time_seconds > 0),
                    source_type TEXT NOT NULL,
                    tags_json TEXT NOT NULL,
                    target_roles_json TEXT NOT NULL,
                    active INTEGER NOT NULL DEFAULT 1 CHECK (active IN (0, 1))
                );
                CREATE INDEX IF NOT EXISTS aptitude_questions_selection_idx
                    ON aptitude_questions(category, difficulty, active);

                CREATE TABLE IF NOT EXISTS aptitude_practice_sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    target_role TEXT NOT NULL,
                    company_type TEXT,
                    experience_level TEXT NOT NULL CHECK (
                        experience_level IN ('Fresher', 'Experienced')
                    ),
                    status TEXT NOT NULL CHECK (status IN ('IN_PROGRESS', 'COMPLETED')),
                    started_at INTEGER NOT NULL,
                    expires_at INTEGER NOT NULL,
                    submitted_at INTEGER,
                    total_questions INTEGER NOT NULL CHECK (total_questions > 0),
                    duration_seconds INTEGER NOT NULL CHECK (duration_seconds > 0),
                    time_taken_seconds INTEGER,
                    correct_answers INTEGER,
                    incorrect_answers INTEGER,
                    unanswered_questions INTEGER,
                    score REAL,
                    accuracy REAL
                );
                CREATE INDEX IF NOT EXISTS aptitude_sessions_user_started_idx
                    ON aptitude_practice_sessions(user_id, started_at DESC);

                CREATE TABLE IF NOT EXISTS aptitude_session_questions (
                    session_id TEXT NOT NULL REFERENCES aptitude_practice_sessions(id) ON DELETE CASCADE,
                    question_id TEXT NOT NULL REFERENCES aptitude_questions(id),
                    ordinal INTEGER NOT NULL CHECK (ordinal >= 0),
                    PRIMARY KEY (session_id, question_id),
                    UNIQUE (session_id, ordinal)
                );

                CREATE TABLE IF NOT EXISTS aptitude_practice_answers (
                    session_id TEXT NOT NULL,
                    question_id TEXT NOT NULL,
                    selected_option INTEGER CHECK (selected_option BETWEEN 0 AND 3),
                    marked_for_review INTEGER NOT NULL DEFAULT 0 CHECK (marked_for_review IN (0, 1)),
                    answered_at INTEGER,
                    is_correct INTEGER CHECK (is_correct IN (0, 1) OR is_correct IS NULL),
                    PRIMARY KEY (session_id, question_id),
                    FOREIGN KEY (session_id, question_id)
                        REFERENCES aptitude_session_questions(session_id, question_id)
                        ON DELETE CASCADE
                );
                CREATE INDEX IF NOT EXISTS aptitude_answers_question_history_idx
                    ON aptitude_practice_answers(question_id, is_correct);

                CREATE TABLE IF NOT EXISTS technical_interview_sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    target_role TEXT NOT NULL,
                    experience_level TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'IN_PROGRESS'
                        CHECK (status IN ('IN_PROGRESS', 'COMPLETED')),
                    total_questions INTEGER NOT NULL,
                    current_index INTEGER NOT NULL DEFAULT 0,
                    started_at INTEGER NOT NULL,
                    completed_at INTEGER
                );
                CREATE TABLE IF NOT EXISTS technical_session_questions (
                    session_id TEXT NOT NULL REFERENCES technical_interview_sessions(id) ON DELETE CASCADE,
                    question_id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    PRIMARY KEY (session_id, question_id)
                );
                CREATE TABLE IF NOT EXISTS technical_session_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES technical_interview_sessions(id) ON DELETE CASCADE,
                    question_id TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    method TEXT NOT NULL,
                    correctness TEXT NOT NULL,
                    strengths TEXT NOT NULL,
                    missing_concepts TEXT NOT NULL,
                    suggestions TEXT NOT NULL,
                    ideal_answer TEXT NOT NULL,
                    answered_at INTEGER NOT NULL
                );

                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL REFERENCES job_posts(id) ON DELETE CASCADE,
                    candidate_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    status TEXT NOT NULL DEFAULT 'APPLIED'
                        CHECK (status IN ('APPLIED', 'REVIEWED', 'SHORTLISTED', 'REJECTED')),
                    score INTEGER,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(job_id, candidate_id)
                );
                CREATE INDEX IF NOT EXISTS job_applications_job_idx ON job_applications(job_id);
                CREATE INDEX IF NOT EXISTS job_applications_candidate_idx ON job_applications(candidate_id);
                """
            )
            columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(users)").fetchall()
            }
            if "role" not in columns:
                connection.execute(
                    """
                    ALTER TABLE users ADD COLUMN role TEXT NOT NULL DEFAULT 'CANDIDATE'
                        CHECK (role IN ('CANDIDATE', 'RECRUITER'))
                    """
                )
            for column, definition in (
                ("phone", "TEXT"),
                ("supabase_user_id", "TEXT"),
            ):
                if column not in columns:
                    connection.execute(f"ALTER TABLE users ADD COLUMN {column} {definition}")
            from src.aptitude.bank import QUESTION_BANK

            connection.executemany(
                """
                INSERT INTO aptitude_questions (
                    id, question, options_json, correct_answer, explanation, topic, subtopic,
                    category, difficulty, estimated_time_seconds, source_type, tags_json,
                    target_roles_json
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    question = excluded.question,
                    options_json = excluded.options_json,
                    correct_answer = excluded.correct_answer,
                    explanation = excluded.explanation,
                    topic = excluded.topic,
                    subtopic = excluded.subtopic,
                    category = excluded.category,
                    difficulty = excluded.difficulty,
                    estimated_time_seconds = excluded.estimated_time_seconds,
                    source_type = excluded.source_type,
                    tags_json = excluded.tags_json,
                    target_roles_json = excluded.target_roles_json
                WHERE NOT EXISTS (
                    SELECT 1
                    FROM aptitude_session_questions
                    WHERE aptitude_session_questions.question_id = aptitude_questions.id
                )
                """,
                [
                    (
                        question["id"],
                        question["question"],
                        json.dumps(question["options"]),
                        question["correct_answer"],
                        question["explanation"],
                        question["topic"],
                        question["subtopic"],
                        question["category"],
                        question["difficulty"],
                        question["estimated_time_seconds"],
                        question["source_type"],
                        json.dumps(question["tags"]),
                        json.dumps(question["target_roles"]),
                    )
                    for question in QUESTION_BANK
                ],
            )
    finally:
        connection.close()
