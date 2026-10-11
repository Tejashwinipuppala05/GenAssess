from __future__ import annotations

import json
import os
import re

from .models import Evaluation, Question


class AnswerEvaluator:
    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL") or None

    def evaluate(self, question: Question, answer: str) -> Evaluation:
        if not answer or not answer.strip():
            raise ValueError("Please enter an answer before submitting.")
        if self.api_key:
            try:
                return self._evaluate_with_llm(question, answer)
            except Exception:
                pass
        return self._rule_based(question, answer)

    def _evaluate_with_llm(self, question: Question, answer: str) -> Evaluation:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model, temperature=0.2,
            messages=[{"role": "system", "content": "Return only valid JSON. Assess a technical answer fairly. score must be integer 0-100."}, {"role": "user", "content": f"Question: {question.prompt}\nExpected concepts: {question.key_concepts}\nIdeal answer: {question.ideal_answer}\nCandidate answer: {answer}\nReturn score, correctness, strengths (array), missing_concepts (array), suggestions (array), ideal_answer."}],
        )
        data = json.loads(response.choices[0].message.content or "")
        score = int(data["score"])
        if not 0 <= score <= 100:
            raise ValueError("Invalid LLM score")
        to_list = lambda value: [str(item) for item in value] if isinstance(value, list) else (_ for _ in ()).throw(ValueError("Expected list"))
        return Evaluation(score, str(data["correctness"]), to_list(data["strengths"]), to_list(data["missing_concepts"]), to_list(data["suggestions"]), str(data["ideal_answer"]), "LLM evaluation")

    def _rule_based(self, question: Question, answer: str) -> Evaluation:
        normalized = re.sub(r"[^a-z0-9+#]", " ", answer.lower())
        matches = [concept for concept in question.key_concepts if concept.lower() in normalized]
        missing = [concept for concept in question.key_concepts if concept not in matches]
        score = min(100, 20 + round(70 * len(matches) / len(question.key_concepts)) + (10 if len(answer.split()) >= 25 else 0))
        strengths = [f"Mentioned: {concept}" for concept in matches] or ["You attempted an answer, but it did not match the reference concepts yet."]
        correctness = "Strong alignment with the reference concepts." if score >= 75 else "Partial alignment with the reference concepts." if score >= 45 else "Limited alignment with the reference concepts."
        suggestions = [f"Address these concepts: {', '.join(missing)}.", "Explain the reasoning with a concrete example."] if missing else ["Keep answers concise and support the concepts with an example."]
        return Evaluation(score, correctness, strengths, missing, suggestions, question.ideal_answer, "Rule-based fallback")
