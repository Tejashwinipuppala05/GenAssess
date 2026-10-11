from __future__ import annotations

from typing import Literal, TypedDict

PracticeRound = Literal["technical", "coding", "behavioral"]


class _BankQuestionRequired(TypedDict):
    id: str
    question: str
    category: str
    topic: str
    difficulty: str
    source: str
    license: str


class BankQuestion(_BankQuestionRequired, total=False):
    round: PracticeRound
    options: list[str]
    correct_answer: str | int
    explanation: str
    estimated_time_seconds: int
    tags: list[str]
    reference_solution: str
    test_cases: list[str]
    test_imports: list[str]
    attribution: str
    follow_up_dimensions: list[str]
    evaluation_criteria: list[str]
