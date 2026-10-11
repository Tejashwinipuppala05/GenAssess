from __future__ import annotations

import pytest

from src.aptitude.bank import QUESTION_BANK
from src.question_banks import (
    BEHAVIORAL_QUESTIONS,
    CODING_QUESTIONS,
    ROUND_BANKS,
    TECHNICAL_QUESTIONS,
    get_category_counts,
    get_round_question_counts,
    validate_question_bank,
)
from src.question_banks.models import BankQuestion
from src.question_banks.source_audit import SOURCE_AUDIT


def test_question_banks_have_expected_round_counts_and_coverage():
    assert get_round_question_counts() == {
        "aptitude": 71,
        "technical": 20,
        "coding": 5,
        "behavioral": 50,
    }
    assert len(QUESTION_BANK) == 71
    assert get_category_counts("technical") == {
        "Python": 2,
        "Java": 2,
        "C/C++": 2,
        "OOP": 2,
        "DBMS": 2,
        "SQL": 2,
        "Operating Systems": 2,
        "Computer Networks": 2,
        "DSA": 2,
        "Software Engineering": 2,
    }
    assert get_category_counts("behavioral") == {
        "Introduction": 5,
        "Teamwork": 5,
        "Leadership": 5,
        "Conflict Resolution": 5,
        "Problem Solving": 5,
        "Communication": 5,
        "Adaptability": 5,
        "Failure/Learning": 5,
        "Workplace Situations": 5,
        "Role-Specific Situations": 5,
    }


def test_new_banks_have_valid_metadata_and_unique_ids():
    all_ids = [question["id"] for questions in ROUND_BANKS.values() for question in questions]
    assert len(all_ids) == len(set(all_ids))
    for questions in ROUND_BANKS.values():
        validate_question_bank(questions)
        assert all(question.get("source") and question.get("license") for question in questions)


def test_mbpp_questions_preserve_attribution_solutions_and_tests_as_data():
    assert len(CODING_QUESTIONS) == 5
    for question in CODING_QUESTIONS:
        assert question["license"] == "CC-BY-4.0"
        assert "MBPP" in question["source"]
        assert question["attribution"]
        assert question["reference_solution"]
        assert len(question["test_cases"]) == 3
        assert question["test_imports"] is not None
        assert all(isinstance(test, str) for test in question["test_cases"])


def test_behavioral_questions_are_original_and_ready_for_follow_up_evaluation():
    assert len(BEHAVIORAL_QUESTIONS) == 50
    for question in BEHAVIORAL_QUESTIONS:
        assert question["source"] == "Original GenAssess question"
        assert question["follow_up_dimensions"]
        assert question["evaluation_criteria"]


def test_question_bank_validator_rejects_duplicate_ids():
    question: BankQuestion = {
        "id": "duplicate",
        "question": "A question?",
        "category": "Python",
        "topic": "Basics",
        "difficulty": "Easy",
        "source": "Original GenAssess question",
        "license": "GenAssess original",
    }

    with pytest.raises(ValueError, match="Duplicate question id"):
        validate_question_bank([question, question])


def test_source_audit_records_incompatible_aptitude_dataset_without_changing_bank():
    assert SOURCE_AUDIT["aptitude"]["available_rows"] == 1769
    assert SOURCE_AUDIT["aptitude"]["inspected_rows"] == 1769
    assert SOURCE_AUDIT["aptitude"]["imported_rows"] == 0
    assert "choices" in SOURCE_AUDIT["aptitude"]["decision"]
    assert len(QUESTION_BANK) == 71


def test_round_bank_registry_is_only_data_and_has_no_submission_executor():
    assert set(ROUND_BANKS) == {"technical", "coding", "behavioral"}
    assert all(callable(value) is False for value in ROUND_BANKS.values())
    assert len(TECHNICAL_QUESTIONS) == 20
