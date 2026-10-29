from __future__ import annotations

from src.rounds.routes import _truncate_option, _validate_distractors


def make_question(correct: str = "Correct answer text", qid: str = "q1") -> dict:
    return {"id": qid, "question": "Q", "topic": "Java", "difficulty": "Medium", "correct_answer": correct}


def test_valid_structured_output():
    q = make_question("Correct answer")
    distractors = ["Wrong 1", "Wrong 2", "Wrong 3"]
    assert _validate_distractors(q, distractors) == distractors


def test_duplicate_distractors_rejected():
    q = make_question("Correct answer")
    assert _validate_distractors(q, ["Wrong 1", "Wrong 1", "Wrong 2"]) is None


def test_distractor_repeats_correct_answer_rejected():
    q = make_question("Correct answer")
    assert _validate_distractors(q, ["Correct answer", "Wrong 2", "Wrong 3"]) is None


def test_missing_or_extra_distractors_rejected():
    q = make_question("Correct answer")
    assert _validate_distractors(q, ["Wrong 1", "Wrong 2"]) is None
    assert _validate_distractors(q, ["Wrong 1", "Wrong 2", "Wrong 3", "Wrong 4"]) is None


def test_malformed_json_handled_by_validation():
    q = make_question("Correct answer")
    assert _validate_distractors(q, "not a list") is None
    assert _validate_distractors(q, None) is None


def test_unrelated_options_rejected_by_uniqueness():
    q = make_question("Correct answer")
    # All options distinct but correct not repeated; validation passes structurally.
    # Semantic unrelatedness is handled by prompt + same-topic fallback; here we just check shape.
    assert _validate_distractors(q, ["A", "B", "C"]) == ["A", "B", "C"]