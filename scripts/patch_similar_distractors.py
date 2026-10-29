p='src/rounds/routes.py'
s=open(p).read()

# Add helper for word-overlap similarity before _llm_distractors
old_helper='''def _llm_distractors(question: dict[str, Any]) -> list[str] | None:'''
new_helper='''def _word_overlap(a: str, b: str) -> float:
    sa = {w.lower() for w in a.split() if len(w) > 3}
    sb = {w.lower() for w in b.split() if len(w) > 3}
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / len(sa | sb)


def _similar_distractors(question: dict[str, Any], bank: list[dict[str, Any]]) -> list[str]:
    correct = question["correct_answer"]
    candidates = [
        q["correct_answer"]
        for q in bank
        if q["correct_answer"] != correct and q["category"] == question["category"]
    ]
    if len(candidates) < 3:
        candidates = [q["correct_answer"] for q in bank if q["correct_answer"] != correct]
    scored = sorted(candidates, key=lambda a: _word_overlap(correct, a), reverse=True)
    # Pick top similar but ensure diversity.
    chosen: list[str] = []
    for answer in scored:
        if answer not in chosen:
            chosen.append(answer)
        if len(chosen) == 3:
            break
    if len(chosen) < 3:
        for answer in candidates:
            if answer not in chosen:
                chosen.append(answer)
            if len(chosen) == 3:
                break
    return [_truncate_option(a) for a in chosen]


def _llm_distractors(question: dict[str, Any]) -> list[str] | None:'''
assert old_helper in s
s=s.replace(old_helper,new_helper,1)

# Update fallback in list_questions to use _similar_distractors
old='''                if distractors is None:
                    same_category = [
                        _truncate_option(q["correct_answer"])
                        for q in bank
                        if q["category"] == question["category"] and q["correct_answer"] != question["correct_answer"]
                    ]
                    pool = same_category if len(same_category) >= 3 else [_truncate_option(a) for a in all_answers if a != question["correct_answer"]]
                    distractors = rng.sample(pool, min(3, len(pool)))'''
new='''                if distractors is None:
                    distractors = _similar_distractors(question, bank)'''
assert old in s
s=s.replace(old,new,1)

# Update fallback in evaluate_technical
old2='''            same_category = [
                _truncate_option(q["correct_answer"])
                for q in TECHNICAL_QUESTIONS
                if q["category"] == question_data["category"] and q["correct_answer"] != question_data["correct_answer"]
            ]
            pool = same_category if len(same_category) >= 3 else [_truncate_option(a) for a in all_answers if a != question_data["correct_answer"]]
            distractors = random.sample(pool, min(3, len(pool)))
            options = distractors + [correct]'''
new2='''            distractors = _similar_distractors(question_data, TECHNICAL_QUESTIONS)
            options = distractors + [correct]'''
assert old2 in s
s=s.replace(old2,new2,1)

open(p,'w').write(s)
print('done')