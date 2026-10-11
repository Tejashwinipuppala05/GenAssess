import pytest

from src.evaluator import AnswerEvaluator
from src.interview import InterviewSession
from src.question_bank import fallback_question


def test_local_question_fallback_is_labeled():
    question = fallback_question("Python", "Easy", set())
    assert question.source == "Local question bank"
    assert question.topic == "Python"


def test_fallback_avoids_a_previously_used_question_when_available():
    first = fallback_question("Python", "Easy", set())
    second = fallback_question("Python", "Easy", {first.prompt})
    assert second.prompt != first.prompt


def test_empty_answer_is_rejected():
    question = fallback_question("SQL", "Easy", set())
    with pytest.raises(ValueError, match="enter an answer"):
        AnswerEvaluator().evaluate(question, "  ")


def test_rule_based_score_detects_concepts(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    question = fallback_question("Python", "Easy", set())
    result = AnswerEvaluator().evaluate(question, "A list is mutable, while a tuple is immutable. A tuple cannot be changed.")
    assert result.method == "Rule-based fallback"
    assert result.score >= 80


def test_interview_progression_adapts_after_good_score(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    session = InterviewSession("Software Engineer", "Python", "Easy", 2)
    session.start()
    session.submit("A list is mutable, while a tuple is immutable. Both list and tuple are sequences.")
    session.next()
    assert session.current_difficulty == "Medium"
    assert len(session.records) == 1


def test_final_score_calculation(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    session = InterviewSession("Software Engineer", "SQL", "Easy", 1)
    session.start()
    session.submit("WHERE filters rows before a group aggregate; HAVING filters groups after aggregate.")
    assert session.is_complete
    assert session.summary()["average"] == session.records[0].evaluation.score
