p='src/rounds/routes.py'
s=open(p).read()
helper='''

def _truncate_option(text: str, limit: int = 280) -> str:
    text = " ".join(str(text).split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


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
    prompt = (
        "You are creating a multiple-choice technical interview question. "
        "Generate exactly 3 plausible but incorrect answer options for the question below. "
        "They must be in the same domain and similar length to the correct answer, "
        "but factually wrong or misleading. Return only a JSON array of 3 strings.\\n\\n"
        f"Question: {question['question']}\\n"
        f"Correct answer: {question['correct_answer']}\\n"
        f"Topic: {question['topic']}\\n"
        f"Category: {question['category']}"
    )
    try:
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
        )
        content = response.choices[0].message.content or ""
        start = content.find("[")
        end = content.rfind("]")
        if start == -1 or end == -1:
            return None
        options = json.loads(content[start : end + 1])
        if not isinstance(options, list) or len(options) != 3:
            return None
        cleaned = [_truncate_option(str(item)) for item in options]
        correct = _truncate_option(question["correct_answer"])
        if any(not item or item.lower() == correct.lower() for item in cleaned):
            return None
        if len(set(item.lower() for item in cleaned)) != 3:
            return None
        return cleaned
    except Exception:
        return None
'''
s=s.replace("def list_questions(", helper + "\ndef list_questions(", 1)
open(p,'w').write(s)
print('done')