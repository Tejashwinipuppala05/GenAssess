from __future__ import annotations

import os
import json
import logging

import random
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, ConfigDict, Field

from src.auth.authorization import require_role
from src.auth.models import User, UserRole
from src.evaluator import AnswerEvaluator
from src.models import Question
from src.question_banks import (
    BEHAVIORAL_QUESTIONS,
    CODING_QUESTIONS,
    TECHNICAL_QUESTIONS,
    execute_python_test_cases,
)

router = APIRouter(prefix="/candidate/practice/rounds", tags=["candidate practice rounds"])
logger = logging.getLogger("genassess.technical_mcq")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(_handler)
evaluator = AnswerEvaluator()
_TECHNICAL_OPTION_ANSWERS: dict[str, int] = {}
_TECHNICAL_OPTIONS_CACHE: dict[str, list[str]] = {}


class RoundQuestion(BaseModel):
    id: str
    question: str
    topic: str
    category: str
    difficulty: str
    source: str
    license: str
    options: list[str] | None = None
    test_cases: list[str] | None = None
    follow_up_dimensions: list[str] | None = None

    model_config = ConfigDict(populate_by_name=True)


class EvaluateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    question_id: str = Field(alias="questionId")
    answer: str = ""
    selected_answer: int | None = Field(default=None, alias="selectedAnswer")


class EvaluateResponse(BaseModel):
    question_id: str = Field(serialization_alias="questionId")
    score: int
    method: str
    correctness: str
    strengths: list[str]
    missing_concepts: list[str] = Field(serialization_alias="missingConcepts")
    suggestions: list[str]
    model_config = ConfigDict(populate_by_name=True)


class CodeRunRequest(BaseModel):
    model_config = ConfigDict(extra="forbid", populate_by_name=True)
    question_id: str = Field(alias="questionId")
    code: str


class CodeRunResponse(BaseModel):
    question_id: str = Field(serialization_alias="questionId")
    passed: bool
    returncode: int | None
    stdout: str
    stderr: str
    model_config = ConfigDict(populate_by_name=True)


def _bank(round_name: str) -> list[dict[str, Any]]:
    if round_name == "technical":
        return TECHNICAL_QUESTIONS
    if round_name == "coding":
        return CODING_QUESTIONS
    if round_name == "behavioral":
        return BEHAVIORAL_QUESTIONS
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unknown round.")


def _find(round_name: str, question_id: str) -> dict[str, Any]:
    for question in _bank(round_name):
        if question["id"] == question_id:
            return question
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Question not found.")


def _role_tokens(target_role: str) -> set[str]:
    return {token.lower() for token in target_role.replace("/", " ").replace("-", " ").split()}


def _technical_relevant(question: dict[str, Any], target_role: str) -> bool:
    role = target_role.lower()
    category = question["category"].lower()
    topic = question["topic"].lower()
    if "data" in role or "analytics" in role:
        return category in {"sql", "dbms", "dsa", "software engineering", "cloud"} or any(
            keyword in topic for keyword in ("sql", "database", "data", "query", "table")
        )
    if "ai" in role or "machine learning" in role or "ml" in role:
        return category in {"dsa", "software engineering", "cloud", "python"} or any(
            keyword in topic for keyword in ("algorithm", "data", "python", "model")
        )
    # Default: software engineering roles.
    return True


def _coding_relevant(question: dict[str, Any], target_role: str) -> bool:
    role = target_role.lower()
    topic = question["topic"].lower()
    if "data" in role or "analytics" in role:
        return topic in {"lists", "mathematics", "algorithms"} or "list" in topic or "math" in topic
    if "ai" in role or "machine learning" in role or "ml" in role:
        return topic in {"algorithms", "mathematics", "lists"} or "algorithm" in topic
    return True


def _truncate_option(text: str, limit: int = 120) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."




def _word_overlap(a: str, b: str) -> float:
    sa = {w.lower() for w in a.split() if len(w) > 3}
    sb = {w.lower() for w in b.split() if len(w) > 3}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _similar_distractors(question: dict[str, Any], bank: list[dict[str, Any]]) -> list[str]:
    correct = question["correct_answer"]
    topic_candidates = [
        q["correct_answer"]
        for q in bank
        if q["correct_answer"] != correct and q["topic"] == question["topic"]
    ]
    # Require at least some word overlap with the correct answer.
    relevant = [a for a in topic_candidates if _word_overlap(correct, a) >= 0.15]
    if len(relevant) >= 3:
        candidates = relevant
    else:
        return None
    if len(candidates) < 3:
        return None
    scored = sorted(candidates, key=lambda a: _word_overlap(correct, a), reverse=True)
    chosen: list[str] = []
    for answer in scored:
        if answer not in chosen:
            chosen.append(answer)
        if len(chosen) == 3:
            break
    if len(chosen) < 3:
        return None
    return [_truncate_option(a) for a in chosen]

def _validate_distractors(question: dict[str, Any], distractors: Any) -> list[str] | None:
    if not isinstance(distractors, list) or len(distractors) != 3:
        return None
    cleaned = [_truncate_option(str(item)) for item in distractors]
    correct = _truncate_option(question["correct_answer"])
    if any(not item for item in cleaned):
        return None
    if any(item.lower() == correct.lower() for item in cleaned):
        return None
    if len(set(item.lower() for item in cleaned)) != 3:
        return None
    if len(set(item.lower() for item in cleaned) | {correct.lower()}) != 4:
        return None
    return cleaned


def _llm_distractors(question: dict[str, Any]) -> list[str] | None:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.info("LLM distractor generation skipped: OPENAI_API_KEY is not configured.")
        return None
    logger.info("LLM distractor generation using configured OpenAI-compatible endpoint with model %s.", os.getenv("OPENAI_MODEL", "gpt-4o-mini"))
    try:
        from openai import OpenAI
    except Exception:
        return None
    client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)
    model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    schema = {
        "question_id": question["id"],
        "topic": question["topic"],
        "difficulty": question["difficulty"],
        "correct_answer": question["correct_answer"],
        "distractors": ["string", "string", "string"],
        "explanation": "string",
    }
    prompt = (
        "You are a strict JSON generator for technical interview MCQs. "
        "Return only valid JSON matching this schema: "
        + json.dumps(schema)
        + "\n\n"
        "Rules:\n"
        "- Generate exactly 3 plausible but incorrect distractors.\n"
        "- Distractors must directly answer the same question.\n"
        "- Distractors must be relevant to the topic and difficulty.\n"
        "- Distractors must not repeat the correct answer.\n"
        "- Distractors must be distinct from each other.\n"
        "- Do not rewrite the question or change the correct answer.\n"
        "- Keep options concise.\n\n"
        f"Question: {question['question']}\n"
        f"Topic: {question['topic']}\n"
        f"Difficulty: {question['difficulty']}\n"
        f"Correct answer: {question['correct_answer']}"
    )
    for _ in range(2):
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            data = json.loads(content)
            distractors = data.get("distractors")
            validated = _validate_distractors(question, distractors)
            if validated is not None:
                logger.info("LLM distractor generation succeeded for %s.", question["id"])
                return validated
            logger.warning("LLM distractor validation failed for %s.", question["id"])
        except Exception as exc:
            logger.warning("LLM distractor generation error for %s: %s", question["id"], exc)
            continue
    return None

@router.get("/{round_name}/questions", response_model=list[RoundQuestion])
def list_questions(
    round_name: str,
    limit: int = 5,
    target_role: str = Query(default="Software Engineer"),
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))] = None,
) -> list[RoundQuestion]:
    bank = _bank(round_name)
    if round_name == "technical":
        filtered = [q for q in bank if _technical_relevant(q, target_role)]
    elif round_name == "coding":
        filtered = [q for q in bank if _coding_relevant(q, target_role)]
    else:
        filtered = bank
    if not filtered:
        filtered = bank
    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))

    if round_name == "technical":
        for question in chosen:
            qid = question["id"]
            if qid in _TECHNICAL_OPTIONS_CACHE:
                options = _TECHNICAL_OPTIONS_CACHE[qid]
            else:
                correct = _truncate_option(question["correct_answer"])
                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("Using heuristic distractors for %s (LLM unavailable/invalid).", question["id"])
                    distractors = _similar_distractors(question, bank)
                if distractors is None:
                    logger.info("No relevant distractors for %s; marking as descriptive.", question["id"])
                    question["_options"] = None
                    continue
                options = distractors + [correct]
                rng.shuffle(options)
                options.append("I don't know")
                _TECHNICAL_OPTIONS_CACHE[qid] = options
            if options is not None:
                _TECHNICAL_OPTION_ANSWERS[qid] = options.index(_truncate_option(question["correct_answer"]))
            question["_options"] = options
    result = []
    for question in chosen:
        result.append(
            RoundQuestion(
                id=question["id"],
                question=question["question"],
                topic=question["topic"],
                category=question["category"],
                difficulty=question["difficulty"],
                source=question["source"],
                license=question["license"],
                options=question.get("_options"),
                test_cases=question.get("test_cases"),
                follow_up_dimensions=question.get("follow_up_dimensions"),
            )
        )
    return result


@router.post("/technical/evaluate", response_model=EvaluateResponse)
def evaluate_technical(
    payload: EvaluateRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
) -> EvaluateResponse:
    question_data = _find("technical", payload.question_id)
    if payload.selected_answer is not None and payload.question_id in _TECHNICAL_OPTION_ANSWERS:
        correct_index = _TECHNICAL_OPTION_ANSWERS[payload.question_id]
        is_correct = payload.selected_answer == correct_index
        score = 100 if is_correct else 0
        return EvaluateResponse(
            question_id=payload.question_id,
            score=score,
            method="Multiple-choice",
            correctness="Correct" if is_correct else "Incorrect",
            strengths=["Selected the correct option."] if is_correct else [],
            missing_concepts=[] if is_correct else ["Review the selected concept."],
            suggestions=[] if is_correct else ["Try again and review the topic."],
        )
    # If no MCQ options are available, fall back to descriptive evaluation.
    question = Question(
        prompt=question_data["question"],
        topic=question_data["topic"],
        difficulty=question_data["difficulty"],
        key_concepts=[question_data["topic"]],
        ideal_answer=question_data["correct_answer"],
        source="Local question bank",
    )
    evaluation = evaluator.evaluate(question, payload.answer)
    return EvaluateResponse(
        question_id=payload.question_id,
        score=evaluation.score,
        method=evaluation.method,
        correctness=evaluation.correctness,
        strengths=evaluation.strengths,
        missing_concepts=evaluation.missing_concepts,
        suggestions=evaluation.suggestions,
    )


@router.post("/behavioral/evaluate", response_model=EvaluateResponse)
def evaluate_behavioral(
    payload: EvaluateRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
) -> EvaluateResponse:
    question_data = _find("behavioral", payload.question_id)
    question = Question(
        prompt=question_data["question"],
        topic=question_data["topic"],
        difficulty=question_data["difficulty"],
        key_concepts=question_data.get("follow_up_dimensions", []),
        ideal_answer="",
        source="Local question bank",
    )
    evaluation = evaluator.evaluate(question, payload.answer)
    return EvaluateResponse(
        question_id=payload.question_id,
        score=evaluation.score,
        method=evaluation.method,
        correctness=evaluation.correctness,
        strengths=evaluation.strengths,
        missing_concepts=evaluation.missing_concepts,
        suggestions=evaluation.suggestions,
    )


@router.post("/coding/run", response_model=CodeRunResponse)
def run_coding(
    payload: CodeRunRequest,
    user: Annotated[User, Depends(require_role(UserRole.CANDIDATE))],
) -> CodeRunResponse:
    question_data = _find("coding", payload.question_id)
    result = execute_python_test_cases(
        payload.code,
        question_data["test_cases"],
        test_imports=question_data.get("test_imports", []),
    )
    return CodeRunResponse(
        question_id=payload.question_id,
        passed=result["passed"],
        returncode=result["returncode"],
        stdout=result["stdout"],
        stderr=result["stderr"],
    )
