from __future__ import annotations

import json
import os
import random
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from .bank import QuestionDefinition

CATEGORIES = (
    "Quantitative Aptitude",
    "Logical Reasoning",
    "Verbal Ability",
    "Non-verbal Reasoning",
)
DIFFICULTIES = ("Easy", "Medium", "Hard")
DEFAULT_CATEGORY_COUNTS = {
    "Quantitative Aptitude": 8,
    "Logical Reasoning": 6,
    "Verbal Ability": 6,
}
DEFAULT_DIFFICULTY_DISTRIBUTION = {"Easy": 30, "Medium": 50, "Hard": 20}


@dataclass(frozen=True)
class SelectionConfig:
    category_counts: dict[str, int]
    difficulty_distribution: dict[str, int]

    @property
    def question_count(self) -> int:
        return sum(self.category_counts.values())


def _load_json_setting(name: str, default: dict[str, int]) -> dict[str, int]:
    raw_value = os.getenv(name)
    if not raw_value:
        return default.copy()
    try:
        value = json.loads(raw_value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"{name} must contain a JSON object of integer values.") from exc
    if not isinstance(value, dict) or not all(
        isinstance(key, str) and isinstance(count, int) and not isinstance(count, bool)
        for key, count in value.items()
    ):
        raise ValueError(f"{name} must contain a JSON object of integer values.")
    return value


def load_selection_config() -> SelectionConfig:
    category_counts = _load_json_setting("APTITUDE_CATEGORY_COUNTS", DEFAULT_CATEGORY_COUNTS)
    distribution = _load_json_setting(
        "APTITUDE_DIFFICULTY_DISTRIBUTION",
        DEFAULT_DIFFICULTY_DISTRIBUTION,
    )
    if (
        not category_counts
        or any(category not in CATEGORIES for category in category_counts)
        or any(count < 1 for count in category_counts.values())
        or sum(category_counts.values()) > 80
    ):
        raise ValueError(
            "APTITUDE_CATEGORY_COUNTS must include supported categories with counts from 1 to 80 total."
        )
    if (
        set(distribution) != set(DIFFICULTIES)
        or any(weight < 0 for weight in distribution.values())
        or sum(distribution.values()) != 100
    ):
        raise ValueError(
            "APTITUDE_DIFFICULTY_DISTRIBUTION must define Easy, Medium and Hard percentages totaling 100."
        )
    return SelectionConfig(category_counts, distribution)


def _apportion(total: int, weights: dict[str, int], order: tuple[str, ...]) -> dict[str, int]:
    weight_total = sum(weights.values())
    exact = {key: total * weights[key] / weight_total for key in order}
    counts = {key: int(exact[key]) for key in order}
    remaining = total - sum(counts.values())
    remainders = sorted(order, key=lambda key: (-(exact[key] - counts[key]), order.index(key)))
    for key in remainders[:remaining]:
        counts[key] += 1
    return counts


def adapted_difficulty_distribution(
    base: dict[str, int],
    history: list[dict[str, Any]],
    experience_level: str,
) -> dict[str, int]:
    distribution = base.copy()
    if experience_level == "Experienced":
        shift = min(10, distribution["Easy"])
        distribution["Easy"] -= shift
        distribution["Hard"] += shift

    answered = [attempt for attempt in history if attempt.get("is_correct") is not None]
    if not answered:
        return distribution

    accuracy = sum(bool(attempt["is_correct"]) for attempt in answered) / len(answered)
    if accuracy < 0.5:
        shift = min(10, distribution["Hard"])
        distribution["Hard"] -= shift
        distribution["Easy"] += shift
    elif accuracy >= 0.8:
        shift = min(10, distribution["Easy"])
        distribution["Easy"] -= shift
        distribution["Hard"] += shift
    return distribution


def topic_selection_weights(history: list[dict[str, Any]]) -> dict[str, float]:
    results: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for attempt in history:
        if attempt.get("is_correct") is None:
            continue
        topic = str(attempt["topic"])
        results[topic][0] += int(bool(attempt["is_correct"]))
        results[topic][1] += 1
    weights: dict[str, float] = {}
    for topic, (correct, answered) in results.items():
        accuracy = correct / answered
        weights[topic] = 1.0 + 2.0 * (1.0 - accuracy)
    return weights


def difficulty_quotas(
    count: int,
    distribution: dict[str, int],
    available: dict[str, int],
) -> dict[str, int]:
    quotas = _apportion(count, distribution, DIFFICULTIES)
    for difficulty in DIFFICULTIES:
        while quotas[difficulty] > available.get(difficulty, 0):
            quotas[difficulty] -= 1
            alternatives = [
                candidate
                for candidate in DIFFICULTIES
                if quotas[candidate] < available.get(candidate, 0)
            ]
            if not alternatives:
                raise ValueError("The question bank does not have enough questions for this session pattern.")
            destination = max(alternatives, key=lambda key: (distribution[key], -DIFFICULTIES.index(key)))
            quotas[destination] += 1
    return quotas


def _weighted_sample(
    candidates: list[QuestionDefinition],
    count: int,
    topic_weights: dict[str, float],
    target_role: str,
    rng: random.Random,
) -> list[QuestionDefinition]:
    selected: list[QuestionDefinition] = []
    remaining = candidates.copy()
    role_tokens = set(target_role.lower().replace("/", " ").replace("-", " ").split())
    while remaining and len(selected) < count:
        weights: list[float] = []
        for question in remaining:
            weight = topic_weights.get(question["topic"], 1.0)
            question_role_tokens = {
                token.lower()
                for role in question["target_roles"]
                for token in role.replace("/", " ").replace("-", " ").split()
            }
            if role_tokens and role_tokens.intersection(question_role_tokens):
                weight *= 1.25
            weights.append(weight)
        choice = rng.choices(remaining, weights=weights, k=1)[0]
        selected.append(choice)
        remaining.remove(choice)
    return selected


def _is_external(question: QuestionDefinition) -> bool:
    source_type = str(question.get("source_type", ""))
    return source_type != "Original GenAssess question"


def _external_share() -> int | None:
    raw = os.getenv("APTITUDE_EXTERNAL_QUESTION_SHARE")
    if not raw:
        return None
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError("APTITUDE_EXTERNAL_QUESTION_SHARE must be an integer from 0 to 100.") from exc
    if value < 0 or value > 100:
        raise ValueError("APTITUDE_EXTERNAL_QUESTION_SHARE must be an integer from 0 to 100.")
    return value


def select_questions(
    question_bank: list[QuestionDefinition],
    config: SelectionConfig,
    target_role: str,
    experience_level: str,
    history: list[dict[str, Any]],
    rng: random.Random | None = None,
    external_share: int | None = None,
) -> list[QuestionDefinition]:
    generator = rng or random.SystemRandom()
    if external_share is None:
        external_share = _external_share()
    if external_share == 0:
        question_bank = [question for question in question_bank if not _is_external(question)]
    elif external_share == 100:
        question_bank = [question for question in question_bank if _is_external(question)]
    distribution = adapted_difficulty_distribution(
        config.difficulty_distribution,
        history,
        experience_level,
    )
    topic_weights = topic_selection_weights(history)
    attempts_by_question: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for attempt in history:
        attempts_by_question[str(attempt["question_id"])].append(attempt)

    selected: list[QuestionDefinition] = []
    selected_ids: set[str] = set()
    for category, category_count in config.category_counts.items():
        category_bank = [question for question in question_bank if question["category"] == category]
        available = {
            difficulty: sum(question["difficulty"] == difficulty for question in category_bank)
            for difficulty in DIFFICULTIES
        }
        quotas = difficulty_quotas(category_count, distribution, available)
        for difficulty, quota in quotas.items():
            pool = [
                question
                for question in category_bank
                if question["difficulty"] == difficulty and question["id"] not in selected_ids
            ]
            never_seen = [question for question in pool if question["id"] not in attempts_by_question]
            previously_seen = [question for question in pool if question["id"] in attempts_by_question]
            previously_seen.sort(
                key=lambda question: (
                    any(
                        attempt.get("is_correct") is True
                        for attempt in attempts_by_question[question["id"]]
                    ),
                    max(attempt.get("attempted_at", 0) for attempt in attempts_by_question[question["id"]]),
                )
            )
            choices = _weighted_sample(
                never_seen,
                min(quota, len(never_seen)),
                topic_weights,
                target_role,
                generator,
            )
            if len(choices) < quota:
                choices.extend(
                    _weighted_sample(
                        previously_seen,
                        quota - len(choices),
                        topic_weights,
                        target_role,
                        generator,
                    )
                )
            selected.extend(choices)
            selected_ids.update(question["id"] for question in choices)

    generator.shuffle(selected)
    return selected
