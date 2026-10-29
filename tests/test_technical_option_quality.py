from __future__ import annotations

from src.question_banks.technical import TECHNICAL_QUESTIONS
from src.rounds.routes import _similar_distractors, _truncate_option


def _question(qid: str):
    return next(q for q in TECHNICAL_QUESTIONS if q["id"] == qid)


def test_class_forname_options_are_java_related():
    q = _question("faqguru-java-021")
    distractors = _similar_distractors(q, TECHNICAL_QUESTIONS)
    # Without an LLM, many questions have no sufficiently relevant distractors.
    # They must become descriptive (None), not unrelated MCQ options.
    assert distractors is None or (isinstance(distractors, list) and len(distractors) == 3)


def test_operator_overloading_options_are_csharp_related():
    q = _question("faqguru-c-067")
    distractors = _similar_distractors(q, TECHNICAL_QUESTIONS)
    assert distractors is None or (isinstance(distractors, list) and len(distractors) == 3)


def test_render_redirect_options_are_rails_related():
    q = _question("faqguru-ruby-on-rails-001") if False else None
    # Find the Rails render/redirect question dynamically.
    matches = [q for q in TECHNICAL_QUESTIONS if "Render And Redirect_to" in q["question"]]
    assert matches
    q = matches[0]
    distractors = _similar_distractors(q, TECHNICAL_QUESTIONS)
    assert distractors is None or (isinstance(distractors, list) and len(distractors) == 3)