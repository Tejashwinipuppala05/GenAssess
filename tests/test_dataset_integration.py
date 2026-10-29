from __future__ import annotations

import json
from pathlib import Path

import pytest

from src.aptitude.bank import QUESTION_BANK as APTITUDE_QUESTIONS
from src.question_banks import (
    BEHAVIORAL_QUESTIONS,
    CODING_QUESTIONS,
    TECHNICAL_QUESTIONS,
    execute_python_test_cases,
    get_round_question_counts,
    validate_question_bank,
)
from src.question_banks.source_audit import SOURCE_AUDIT


def test_dataset_import_counts_are_reported():
    counts = get_round_question_counts()
    assert counts["aptitude"] == 221
    assert counts["technical"] == 1593
    assert counts["coding"] == 120
    assert counts["behavioral"] == 70
    assert SOURCE_AUDIT["aptitude"]["imported_rows"] == 150
    assert SOURCE_AUDIT["mbpp"]["imported_rows"] == 120
    assert SOURCE_AUDIT["software_interview"]["imported_rows"] == 0


def test_imported_aptitude_questions_have_valid_metadata_and_options():
    imported = [q for q in APTITUDE_QUESTIONS if q.get("source_type", "").startswith("Aptitude-QA")]
    assert len(imported) == 150
    for question in imported:
        assert question["category"] == "Verbal Ability"
        assert isinstance(question["options"], list) and len(question["options"]) == 4
        assert isinstance(question["correct_answer"], int)
        assert 0 <= question["correct_answer"] <= 3
        assert question["license"] == "Apache-2.0"
        assert question["attribution"]


def test_coding_questions_pass_actual_execution():
    for question in CODING_QUESTIONS:
        result = execute_python_test_cases(
            question["reference_solution"],
            question["test_cases"],
            test_imports=question.get("test_imports", []),
        )
        assert result["passed"] is True, question["id"]


def test_behavioral_original_questions_are_preserved():
    original = [q for q in BEHAVIORAL_QUESTIONS if q["source"] == "Original GenAssess question"]
    assert len(original) == 70
    assert all(q["follow_up_dimensions"] and q["evaluation_criteria"] for q in original)


def test_duplicate_validation_rejects_duplicate_ids():
    duplicate = dict(CODING_QUESTIONS[0])
    with pytest.raises(ValueError, match="Duplicate question id"):
        validate_question_bank([CODING_QUESTIONS[0], duplicate])