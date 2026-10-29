p='src/rounds/routes.py'
s=open(p).read()

# Replace _llm_distractors function
old_start=s.index('def _llm_distractors(question: dict[str, Any]) -> list[str] | None:')
old_end=s.index('def list_questions(')
old_func=s[old_start:old_end]

new_func='''def _validate_distractors(question: dict[str, Any], distractors: Any) -> list[str] | None:
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
        return None
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
        + "\\n\\n"
        "Rules:\\n"
        "- Generate exactly 3 plausible but incorrect distractors.\\n"
        "- Distractors must directly answer the same question.\\n"
        "- Distractors must be relevant to the topic and difficulty.\\n"
        "- Distractors must not repeat the correct answer.\\n"
        "- Distractors must be distinct from each other.\\n"
        "- Do not rewrite the question or change the correct answer.\\n"
        "- Keep options concise.\\n\\n"
        f"Question: {question['question']}\\n"
        f"Topic: {question['topic']}\\n"
        f"Difficulty: {question['difficulty']}\\n"
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
                return validated
        except Exception:
            continue
    return None

'''
s = s[:old_start] + new_func + s[old_end:]
open(p,'w').write(s)
print('done')