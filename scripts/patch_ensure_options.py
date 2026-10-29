p='src/technical/routes.py'
s=open(p).read()
old='''def _ensure_options(question, bank):
    if question.get("_options"):
        return
    rng = random.SystemRandom()
    all_answers = [q["correct_answer"] for q in bank]
    correct = question["correct_answer"]
    same_category = [q["correct_answer"] for q in bank if q["category"] == question["category"] and q["correct_answer"] != correct]
    pool = same_category if len(same_category) >= 3 else [a for a in all_answers if a != correct]
    distractors = rng.sample(pool, min(3, len(pool)))
    options = distractors + [correct]
    rng.shuffle(options)
    question["_options"] = options
    from src.rounds.routes import _TECHNICAL_OPTION_ANSWERS, _TECHNICAL_OPTIONS_CACHE
    _TECHNICAL_OPTIONS_CACHE[question["id"]] = options
    _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(correct)'''
new='''def _ensure_options(question, bank):
    if question.get("_options"):
        return
    # Try LLM-generated distractors first.
    try:
        from src.rounds.routes import _llm_distractors, _truncate_option
        distractors = _llm_distractors(question)
        if distractors is not None:
            correct = _truncate_option(question["correct_answer"])
            options = distractors + [correct]
            rng = random.SystemRandom()
            rng.shuffle(options)
            options.append("I don't know")
            question["_options"] = options
            from src.rounds.routes import _TECHNICAL_OPTION_ANSWERS, _TECHNICAL_OPTIONS_CACHE
            _TECHNICAL_OPTIONS_CACHE[question["id"]] = options
            _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(correct)
            return
    except Exception:
        pass
    # Fallback: same-category distractors with word overlap.
    rng = random.SystemRandom()
    all_answers = [q["correct_answer"] for q in bank]
    correct = question["correct_answer"]
    same_topic = [q["correct_answer"] for q in bank if q["topic"] == question["topic"] and q["correct_answer"] != correct]
    candidates = [a for a in same_topic if __import__("src.rounds.routes", fromlist=["_word_overlap"])._word_overlap(correct, a) >= 0.15]
    if len(candidates) < 3:
        candidates = same_topic if len(same_topic) >= 3 else [a for a in all_answers if a != correct]
    if len(candidates) < 3:
        question["_options"] = None
        return
    distractors = rng.sample(candidates, min(3, len(candidates)))
    options = [_truncate_option(a) for a in distractors] + [_truncate_option(correct)]
    rng.shuffle(options)
    options.append("I don't know")
    question["_options"] = options
    from src.rounds.routes import _TECHNICAL_OPTION_ANSWERS, _TECHNICAL_OPTIONS_CACHE
    _TECHNICAL_OPTIONS_CACHE[question["id"]] = options
    _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(_truncate_option(correct))'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')