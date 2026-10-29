import json, re, collections
base='data/datasets'
apt=json.load(open(base+'/aptitude.json',encoding='utf-8'))
print('APTITUDE rows',len(apt))
# parse user content
subjects=collections.Counter()
levels=collections.Counter()
cats=collections.Counter()
mcq_like=0
for r in apt:
    user=r['messages'][0]['content']
    # subject line
    m=re.search(r'Subject:\s*(.+)', user)
    subjects[m.group(1).strip() if m else 'NONE']+=1
    m=re.search(r'Level:\s*(.+)', user)
    levels[m.group(1).strip() if m else 'NONE']+=1
    m=re.search(r'Category:\s*(.+)', user)
    cats[m.group(1).strip() if m else 'NONE']+=1
    if re.search(r'\b[A-D]\)|option|choices|^\s*\d+\.', user, re.I):
        mcq_like+=1
print('subjects',subjects)
print('levels',levels)
print('cats sample',cats.most_common(20))
print('mcq_like',mcq_like)
# answer formats
ans_samples=set()
for r in apt:
    a=r['messages'][1]['content']
    # last "Answer:" 
    m=re.search(r'Answer:\s*(.+)', a)
    if m:
        ans_samples.add(m.group(1).strip()[:60])
print('num unique answer snippets',len(ans_samples))
print(list(ans_samples)[:40])