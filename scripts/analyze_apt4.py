import json, re, collections
base='data/datasets'
apt=json.load(open(base+'/aptitude.json',encoding='utf-8'))
opt_style=collections.Counter()
examples=[]
for r in apt:
    user=r['messages'][0]['content']
    if '**Options**' in user or 'Options:' in user:
        opt_style['options_marker']+=1
    # count A) occurrences
    if len(re.findall(r'(?<!\w)[A-D]\)', user))>=3:
        opt_style['3plus_labels']+=1
# subject breakdown for records with at least 3 labels
subj=collections.Counter()
for r in apt:
    user=r['messages'][0]['content']
    if len(re.findall(r'(?<!\w)[A-D]\)', user))>=3:
        m=re.search(r'Subject:\s*(.+)', user)
        subj[m.group(1).strip() if m else 'NONE']+=1
print('options_marker',opt_style['options_marker'])
print('3plus_labels',opt_style['3plus_labels'])
print('subjects with 3+ labels',subj)