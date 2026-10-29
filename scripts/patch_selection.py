p='src/aptitude/selection.py'
s=open(p).read()

# Add helper after imports? os already imported.
# Update select_questions signature
old_sig='''def select_questions(
    question_bank: list[QuestionDefinition],
    config: SelectionConfig,
    target_role: str,
    experience_level: str,
    history: list[dict[str, Any]],
    rng: random.Random | None = None,
) -> list[QuestionDefinition]:'''
new_sig='''def _is_external(question: QuestionDefinition) -> bool:
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
) -> list[QuestionDefinition]:'''
assert old_sig in s
s=s.replace(old_sig,new_sig)

# Apply external_share default from env
old_body='''    generator = rng or random.SystemRandom()
    distribution = adapted_difficulty_distribution('''
new_body='''    generator = rng or random.SystemRandom()
    if external_share is None:
        external_share = _external_share()
    if external_share == 0:
        question_bank = [question for question in question_bank if not _is_external(question)]
    elif external_share == 100:
        question_bank = [question for question in question_bank if _is_external(question)]
    distribution = adapted_difficulty_distribution('''
assert old_body in s
s=s.replace(old_body,new_body)

open(p,'w').write(s)
print('done')