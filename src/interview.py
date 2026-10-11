from __future__ import annotations

from dataclasses import dataclass, field

from .evaluator import AnswerEvaluator
from .models import AnswerRecord, Difficulty, Evaluation, Question
from .question_generator import QuestionGenerator

DIFFICULTIES: list[Difficulty] = ["Easy", "Medium", "Hard"]


@dataclass
class InterviewSession:
    role: str
    topic: str
    initial_difficulty: Difficulty
    total_questions: int
    job_description: str = ""
    generator: QuestionGenerator = field(default_factory=QuestionGenerator)
    evaluator: AnswerEvaluator = field(default_factory=AnswerEvaluator)
    records: list[AnswerRecord] = field(default_factory=list)
    current_question: Question | None = None
    current_difficulty: Difficulty = field(init=False)

    def __post_init__(self) -> None:
        if not 1 <= self.total_questions <= 10:
            raise ValueError("Choose between 1 and 10 questions.")
        self.current_difficulty = self.initial_difficulty

    @property
    def is_complete(self) -> bool:
        return len(self.records) >= self.total_questions

    def start(self) -> Question:
        if self.current_question is None:
            self.current_question = self._new_question()
        return self.current_question

    def submit(self, answer: str) -> Evaluation:
        if self.current_question is None:
            raise ValueError("Start the interview before submitting an answer.")
        if self.records and self.records[-1].question is self.current_question:
            raise ValueError("Move to the next question before submitting another answer.")
        evaluation = self.evaluator.evaluate(self.current_question, answer)
        self.records.append(AnswerRecord(self.current_question, answer.strip(), evaluation))
        return evaluation

    def next(self) -> Question | None:
        if not self.records:
            raise ValueError("Submit an answer before moving to the next question.")
        if self.is_complete:
            self.current_question = None
            return None
        self.current_difficulty = self._adapt(self.records[-1].evaluation.score)
        self.current_question = self._new_question()
        return self.current_question

    def _new_question(self) -> Question:
        return self.generator.generate(self.role, self.topic, self.current_difficulty, self.job_description, {item.question.prompt for item in self.records})

    def _adapt(self, score: int) -> Difficulty:
        index = DIFFICULTIES.index(self.current_difficulty)
        # Transparent MVP policy: >=75 up, <45 down, otherwise unchanged.
        if score >= 75:
            index = min(index + 1, 2)
        elif score < 45:
            index = max(index - 1, 0)
        return DIFFICULTIES[index]

    def summary(self) -> dict[str, object]:
        if not self.records:
            raise ValueError("No evaluated answers are available yet.")
        scores = [item.evaluation.score for item in self.records]
        average = sum(scores) / len(scores)
        label = "Strong" if average >= 75 else "Moderate" if average >= 45 else "Needs improvement"
        return {"average": round(average, 1), "scores": scores, "skill_gaps": {self.topic: label}, "strong": [self.topic] if label == "Strong" else [], "weak": [self.topic] if label == "Needs improvement" else []}
