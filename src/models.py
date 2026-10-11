from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Literal

Difficulty = Literal["Easy", "Medium", "Hard"]


@dataclass(frozen=True)
class Question:
    prompt: str
    topic: str
    difficulty: Difficulty
    key_concepts: list[str]
    ideal_answer: str
    source: Literal["LLM-generated", "Local question bank"]


@dataclass(frozen=True)
class Evaluation:
    score: int
    correctness: str
    strengths: list[str]
    missing_concepts: list[str]
    suggestions: list[str]
    ideal_answer: str
    method: Literal["LLM evaluation", "Rule-based fallback"]


@dataclass(frozen=True)
class AnswerRecord:
    question: Question
    answer: str
    evaluation: Evaluation
    answered_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
