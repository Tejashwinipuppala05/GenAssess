import os
import random
from collections import defaultdict
from datetime import datetime

from src.aptitude.bank import QUESTION_BANK as APTITUDE_QUESTIONS
from src.aptitude.selection import SelectionConfig, load_selection_config, select_questions
from src.evaluator import AnswerEvaluator
from src.models import Question
from src.question_banks import (
    BEHAVIORAL_QUESTIONS,
    CODING_QUESTIONS,
    TECHNICAL_QUESTIONS,
    execute_python_test_cases,
)

rng = random.SystemRandom()
evaluator = AnswerEvaluator()

print("=" * 70)
print("GENASSESS FOUR-ROUND ASSESSMENT DEMO")
print("=" * 70)

# ---------------- Round 1: Aptitude ----------------
print("\nROUND 1 — APTITUDE (MCQ)")
config = load_selection_config()
selected = select_questions(
    APTITUDE_QUESTIONS, config, "Software Engineer", "Fresher", [], rng=rng
)
correct = 0
category_stats = defaultdict(lambda: {"total": 0, "correct": 0})
difficulty_stats = defaultdict(lambda: {"total": 0, "correct": 0})
for q in selected:
    # Simulate a strong candidate: answer correctly 85% of the time.
    answer = q["correct_answer"] if rng.random() < 0.85 else rng.randrange(len(q["options"]))
    is_correct = answer == q["correct_answer"]
    correct += int(is_correct)
    category_stats[q["category"]]["total"] += 1
    category_stats[q["category"]]["correct"] += int(is_correct)
    difficulty_stats[q["difficulty"]]["total"] += 1
    difficulty_stats[q["difficulty"]]["correct"] += int(is_correct)

print(f"Questions: {len(selected)}")
print(f"Score: {correct}/{len(selected)} ({correct / len(selected) * 100:.1f}%)")
print("Category performance:")
for category, stats in sorted(category_stats.items()):
    acc = stats["correct"] / stats["total"] * 100 if stats["total"] else 0
    print(f"  {category}: {stats['correct']}/{stats['total']} ({acc:.0f}%)")
print("Difficulty performance:")
for difficulty in ("Easy", "Medium", "Hard"):
    stats = difficulty_stats[difficulty]
    if stats["total"]:
        acc = stats["correct"] / stats["total"] * 100
        print(f"  {difficulty}: {stats['correct']}/{stats['total']} ({acc:.0f}%)")

# ---------------- Round 2: Technical ----------------
print("\nROUND 2 — TECHNICAL INTERVIEW (Q&A)")
tech_questions = rng.sample(TECHNICAL_QUESTIONS, min(5, len(TECHNICAL_QUESTIONS)))
tech_scores = []
for tq in tech_questions:
    question = Question(
        prompt=tq["question"],
        topic=tq["topic"],
        difficulty=tq["difficulty"],
        key_concepts=[tq["topic"]],
        ideal_answer=tq["correct_answer"],
        source="Local question bank",
    )
    # Sample answer: first sentence of the reference answer.
    answer = tq["correct_answer"].split(".")[0] + "."
    evaluation = evaluator.evaluate(question, answer)
    tech_scores.append(evaluation.score)
    print(f"  Q: {tq['question'][:80]}...")
    print(f"     Score: {evaluation.score}/100 | Method: {evaluation.method}")
print(f"Technical average: {sum(tech_scores) / len(tech_scores):.1f}/100")

# ---------------- Round 3: Coding ----------------
print("\nROUND 3 — CODING CHALLENGE (execution-based)")
coding_questions = rng.sample(CODING_QUESTIONS, min(3, len(CODING_QUESTIONS)))
coding_passed = 0
for cq in coding_questions:
    # Candidate submits the reference solution.
    result = execute_python_test_cases(
        cq["reference_solution"], cq["test_cases"], test_imports=cq.get("test_imports", [])
    )
    coding_passed += int(result["passed"])
    print(f"  Task {cq['id']}: {'PASS' if result['passed'] else 'FAIL'} ({len(cq['test_cases'])} tests)")
    if not result["passed"]:
        print(f"     Error: {result['stderr'][:200]}")
print(f"Coding pass rate: {coding_passed}/{len(coding_questions)}")

# ---------------- Round 4: Behavioral ----------------
print("\nROUND 4 — BEHAVIORAL / HR")
behavioral_questions = rng.sample(BEHAVIORAL_QUESTIONS, min(3, len(BEHAVIORAL_QUESTIONS)))
behavioral_scores = []
for bq in behavioral_questions:
    question = Question(
        prompt=bq["question"],
        topic=bq["topic"],
        difficulty=bq["difficulty"],
        key_concepts=bq.get("follow_up_dimensions", []),
        ideal_answer="",
        source="Local question bank",
    )
    answer = (
        "In a recent project, I faced a challenging situation, took ownership, "
        "collaborated with my team, delivered the outcome, and reflected on what I learned."
    )
    evaluation = evaluator.evaluate(question, answer)
    behavioral_scores.append(evaluation.score)
    print(f"  Q: {bq['question'][:80]}...")
    print(f"     Score: {evaluation.score}/100 | Method: {evaluation.method}")
print(f"Behavioral average: {sum(behavioral_scores) / len(behavioral_scores):.1f}/100")

print("\n" + "=" * 70)
print("ASSESSMENT COMPLETE")
print("=" * 70)