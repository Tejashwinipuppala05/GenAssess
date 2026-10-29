p='src/rounds/routes.py'
s=open(p).read()
old='''    candidates = [
        q["correct_answer"]
        for q in bank
        if q["correct_answer"] != correct and q["topic"] == question["topic"]
    ]
    if len(candidates) < 3:
        candidates = [
            q["correct_answer"]
            for q in bank
            if q["correct_answer"] != correct and q["category"] == question["category"]
        ]
    if len(candidates) < 3:
        candidates = [q["correct_answer"] for q in bank if q["correct_answer"] != correct]'''
new='''    topic_candidates = [
        q["correct_answer"]
        for q in bank
        if q["correct_answer"] != correct and q["topic"] == question["topic"]
    ]
    # Require at least some word overlap with the correct answer.
    relevant = [a for a in topic_candidates if _word_overlap(correct, a) >= 0.05]
    if len(relevant) >= 3:
        candidates = relevant
    elif len(topic_candidates) >= 3:
        candidates = topic_candidates
    else:
        candidates = []'''
assert old in s
s=s.replace(old,new,1)
# After scoring, if fewer than 3 candidates, return None (no MCQ)
s=s.replace('''    scored = sorted(candidates, key=lambda a: _word_overlap(correct, a), reverse=True)
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
    return [_truncate_option(a) for a in chosen]''',
'''    if len(candidates) < 3:
        return None
    scored = sorted(candidates, key=lambda a: _word_overlap(correct, a), reverse=True)
    chosen: list[str] = []
    for answer in scored:
        if answer not in chosen:
            chosen.append(answer)
        if len(chosen) == 3:
            break
    if len(chosen) < 3:
        return None
    return [_truncate_option(a) for a in chosen]''')
open(p,'w').write(s)
print('done')