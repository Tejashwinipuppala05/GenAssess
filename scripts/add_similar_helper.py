p='src/rounds/routes.py'
s=open(p).read()
helper='''

def _word_overlap(a: str, b: str) -> float:
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
'''
s=s.replace("def _llm_distractors(question: dict[str, Any]) -> list[str] | None:", helper + "\ndef _llm_distractors(question: dict[str, Any]) -> list[str] | None:", 1)
open(p,'w').write(s)
print('done')