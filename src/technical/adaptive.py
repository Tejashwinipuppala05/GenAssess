from __future__ import annotations

import random
from typing import Any


def _difficulty_rank(difficulty: str) -> int:
    return {"Easy": 0, "Medium": 1, "Hard": 2}.get(difficulty, 1)


def _rank_to_difficulty(rank: int) -> str:
    rank = max(0, min(2, rank))
    return ("Easy", "Medium", "Hard")[rank]


def select_next_technical_question(
    bank: list[dict[str, Any]],
    used_ids: set[str],
    history: list[dict[str, Any]],
    target_role: str,
    experience_level: str,
    rng: random.Random | None = None,
) -> dict[str, Any] | None:
    generator = rng or random.SystemRandom()
    available = [q for q in bank if q["id"] not in used_ids]
    if not available:
        return None

    # Determine next difficulty from last answer.
    if history:
        last = history[-1]
        last_score = last.get("score", 0)
        last_difficulty = last.get("difficulty", "Medium")
        if last_score >= 80:
            next_rank = _difficulty_rank(last_difficulty) + 1
        elif last_score <= 40:
            next_rank = _difficulty_rank(last_difficulty) - 1
        else:
            next_rank = _difficulty_rank(last_difficulty)
    else:
        # Experienced candidates start one level higher.
        next_rank = 1 if experience_level != "Experienced" else 2

    # Weak-topic prioritization.
    topic_scores: dict[str, list[int]] = {}
    for item in history:
        topic_scores.setdefault(item.get("topic", ""), []).append(item.get("score", 0))
    weak_topics = [
        topic
        for topic, scores in topic_scores.items()
        if scores and (sum(scores) / len(scores)) < 60
    ]

    # Role relevance.
    role = target_role.lower()
    if "data" in role or "analytics" in role:
        preferred_categories = {"sql", "dbms", "dsa", "software engineering", "cloud"}
    elif "ai" in role or "machine learning" in role:
        preferred_categories = {"dsa", "software engineering", "cloud"}
    else:
        preferred_categories = set()

    def score(question: dict[str, Any]) -> float:
        value = 0.0
        if question["difficulty"] == _rank_to_difficulty(next_rank):
            value += 5
        if weak_topics and question["topic"] in weak_topics:
            value += 4
        if preferred_categories and question["category"].lower() in preferred_categories:
            value += 2
        # Slight randomness for variety.
        value += generator.random()
        return value

    available.sort(key=score, reverse=True)
    # Pick from top candidates to avoid always identical.
    top = available[: min(5, len(available))]
    return generator.choice(top)