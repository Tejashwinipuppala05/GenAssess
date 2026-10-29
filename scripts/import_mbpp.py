import json, os, collections
base='data/datasets'
rows=json.load(open(base+'/mbpp_sanitized_train.json',encoding='utf-8'))
existing={602,604,606,608,611}
def topic_for(prompt):
    p=prompt.lower()
    if 'string' in p or 'char' in p or 'vowel' in p or 'substring' in p:
        return 'Strings'
    if 'matrix' in p or 'matrices' in p:
        return 'Matrices'
    if 'list' in p or 'array' in p or 'tuple' in p:
        return 'Lists'
    if 'sort' in p:
        return 'Sorting'
    if 'prime' in p or 'factorial' in p or 'fibonacci' in p or 'number' in p or 'digit' in p or 'sum' in p or 'product' in p or 'gcd' in p or 'lcm' in p:
        return 'Mathematics'
    if 'dict' in p or 'dictionary' in p:
        return 'Dictionaries'
    return 'Algorithms'
def difficulty_for(r):
    code=r['code']
    lines=[l for l in code.splitlines() if l.strip()]
    tests=r['test_list']
    if len(lines)<=4 and len(tests)<=3:
        return 'Easy'
    if len(lines)>=12 or 'def ' in code and code.count('def ')>1 or 'for' in code and 'while' in code:
        return 'Hard'
    return 'Medium'
out=[]
for r in rows:
    if r['task_id'] in existing:
        continue
    out.append({
        'task_id': r['task_id'],
        'topic': topic_for(r['prompt']),
        'difficulty': difficulty_for(r),
        'prompt': r['prompt'],
        'solution': r['code'],
        'tests': r['test_list'],
        'test_imports': r.get('test_imports') or [],
    })
os.makedirs('data/question_banks',exist_ok=True)
json.dump(out, open('data/question_banks/mbpp_validated.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('new records',len(out))
print(collections.Counter(r['topic'] for r in out))
print(collections.Counter(r['difficulty'] for r in out))