import json, re
from collections import Counter, defaultdict
from src.question_banks.technical import TECHNICAL_QUESTIONS

print("Total technical questions:", len(TECHNICAL_QUESTIONS))

# Duplicate IDs
ids = [q["id"] for q in TECHNICAL_QUESTIONS]
dup_ids = [i for i,c in Counter(ids).items() if c>1]
print("Duplicate IDs:", len(dup_ids), dup_ids[:5])

# Duplicate questions (exact)
qtexts = [q["question"].strip().lower() for q in TECHNICAL_QUESTIONS]
dup_qs = [t for t,c in Counter(qtexts).items() if c>1]
print("Duplicate question texts:", len(dup_qs))

# Missing fields
missing = []
for q in TECHNICAL_QUESTIONS:
    for f in ["id","question","topic","difficulty","correct_answer","source","license"]:
        if not q.get(f):
            missing.append((q["id"],f))
print("Missing required fields:", len(missing), missing[:10])

# Difficulty distribution
print("Difficulty:", Counter(q["difficulty"] for q in TECHNICAL_QUESTIONS))

# Category distribution
print("Categories:", Counter(q["category"] for q in TECHNICAL_QUESTIONS))

# Answer length
short = [q["id"] for q in TECHNICAL_QUESTIONS if len(q["correct_answer"]) < 20]
print("Very short answers (<20 chars):", len(short))

# Check for concatenated/unrelated markers
suspicious_markers = ["Angular", "Azure", "React", "CSS Grid", "finally"]
suspicious = []
for q in TECHNICAL_QUESTIONS:
    a = q["correct_answer"]
    for m in suspicious_markers:
        if m in a and m.lower() not in q["topic"].lower() and m.lower() not in q["category"].lower():
            suspicious.append((q["id"], m))
print("Suspicious unrelated markers in answers:", len(suspicious))
print(suspicious[:10])

# Sample 3 per category
by_cat = defaultdict(list)
for q in TECHNICAL_QUESTIONS:
    by_cat[q["category"]].append(q)
print("\nSample questions:")
for cat in sorted(by_cat)[:7]:
    q = by_cat[cat][0]
    print(f"\n[{cat}] {q['id']}")
    print("Q:", q["question"][:120])
    print("A:", q["correct_answer"][:120])