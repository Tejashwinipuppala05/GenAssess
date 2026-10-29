from __future__ import annotations

from collections import Counter
from collections.abc import Iterable

from src.aptitude.bank import QUESTION_BANK as APTITUDE_QUESTIONS

from .behavioral import BEHAVIORAL_QUESTIONS
from .coding import CODING_QUESTIONS
from .models import BankQuestion, PracticeRound
from .technical import TECHNICAL_QUESTIONS
from .execution import execute_python_test_cases


ROUND_BANKS: dict[PracticeRound, list[BankQuestion]] = {
    "technical": TECHNICAL_QUESTIONS,
    "coding": CODING_QUESTIONS,
    "behavioral": BEHAVIORAL_QUESTIONS,
}


def validate_question_bank(questions: Iterable[BankQuestion]) -> None:
    seen_ids: set[str] = set()
    for question in questions:
        required = ("id", "question", "category", "topic", "difficulty", "source", "license")
        missing = [field for field in required if not question.get(field)]
        if missing:
            raise ValueError(f"Question is missing required fields: {', '.join(missing)}.")
        question_id = question["id"]
        if question_id in seen_ids:
            raise ValueError(f"Duplicate question id: {question_id}.")
        seen_ids.add(question_id)
        if question["difficulty"] not in {"Easy", "Medium", "Hard"}:
            raise ValueError(f"Unsupported difficulty for question {question_id}.")
        options = question.get("options")
        if options is not None and (
            not isinstance(options, list) or not all(isinstance(option, str) for option in options)
        ):
            raise ValueError(f"Question {question_id} has invalid options.")
        test_cases = question.get("test_cases")
        if test_cases is not None and not all(isinstance(test, str) for test in test_cases):
            raise ValueError(f"Question {question_id} has invalid test cases.")
        if question.get("round") == "coding" and not question.get("reference_solution"):
            raise ValueError(f"Coding question {question_id} is missing its reference solution.")


def get_round_question_counts() -> dict[str, int]:
    counts = {"aptitude": len(APTITUDE_QUESTIONS)}
    counts.update({round_name: len(questions) for round_name, questions in ROUND_BANKS.items()})
    return counts


def get_category_counts(round_name: PracticeRound) -> dict[str, int]:
    return dict(Counter(question["category"] for question in ROUND_BANKS[round_name]))


for _questions in ROUND_BANKS.values():
    validate_question_bank(_questions)


__all__ = [
    "BEHAVIORAL_QUESTIONS",
    "CODING_QUESTIONS",
    "ROUND_BANKS",
    "TECHNICAL_QUESTIONS",
    "execute_python_test_cases",

    "get_category_counts",
    "get_round_question_counts",
    "validate_question_bank",
]
