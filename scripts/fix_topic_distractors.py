p='src/rounds/routes.py'
s=open(p).read()
# In _similar_distractors, filter by topic instead of category
s=s.replace(
'''    candidates = [
        q["correct_answer"]
        for q in bank
        if q["correct_answer"] != correct and q["category"] == question["category"]
    ]''',
'''    candidates = [
        q["correct_answer"]
        for q in bank
        if q["correct_answer"] != correct and q["topic"] == question["topic"]
    ]''')
# fallback if fewer than 3
s=s.replace(
'''    if len(candidates) < 3:
        candidates = [q["correct_answer"] for q in bank if q["correct_answer"] != correct]''',
'''    if len(candidates) < 3:
        candidates = [
            q["correct_answer"]
            for q in bank
            if q["correct_answer"] != correct and q["category"] == question["category"]
        ]
    if len(candidates) < 3:
        candidates = [q["correct_answer"] for q in bank if q["correct_answer"] != correct]''')
open(p,'w').write(s)
print('done')