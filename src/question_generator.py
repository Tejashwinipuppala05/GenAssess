from __future__ import annotations

import json
import os

from .models import Question
from .question_bank import fallback_question


class QuestionGenerator:
    """Uses an LLM only when configured; API errors safely return a local question."""

    def __init__(self) -> None:
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.base_url = os.getenv("OPENAI_BASE_URL") or None

    def generate(self, role: str, topic: str, difficulty: str, job_description: str, used_prompts: set[str]) -> Question:
        if self.api_key:
            try:
                return self._generate_with_llm(role, topic, difficulty, job_description)
            except Exception:
                pass
        return fallback_question(topic, difficulty, used_prompts)

    def _generate_with_llm(self, role: str, topic: str, difficulty: str, job_description: str) -> Question:
        from openai import OpenAI
        client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        response = client.chat.completions.create(
            model=self.model, temperature=0.4,
            messages=[{"role": "system", "content": "Return only valid JSON with prompt, key_concepts (3-5 strings), and ideal_answer. Write one concise technical interview question."}, {"role": "user", "content": f"Role: {role}\nTopic: {topic}\nDifficulty: {difficulty}\nJob description: {job_description.strip() or 'None supplied'}"}],
        )
        data = json.loads(response.choices[0].message.content or "")
        if not isinstance(data.get("prompt"), str) or not isinstance(data.get("key_concepts"), list) or not isinstance(data.get("ideal_answer"), str):
            raise ValueError("Unexpected LLM question response")
        return Question(data["prompt"].strip(), topic, difficulty, [str(item) for item in data["key_concepts"]], data["ideal_answer"].strip(), "LLM-generated")
