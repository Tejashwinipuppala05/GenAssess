import json, re, collections
base='data/datasets'
apt=json.load(open(base+'/aptitude.json',encoding='utf-8'))
def parse_options(q):
    # find option labels A) ... B) ... etc
    matches=list(re.finditer(r'(?<!\w)([A-D])\)\s*(.*?)(?=(?<!\w)[A-D]\)|$)', q, re.S))
    # require 4 labels in order
    labels=[m.group(1) for m in matches]
    if labels==['A','B','C','D']:
        opts=[m.group(2).strip() for m in matches]
        # remove trailing if option text includes newline? 
        return opts
    return None
cat_counter=collections.Counter()
opt_records=[]
for r in apt:
    user=r['messages'][0]['content']
    qm=re.search(r'Question:\s*(.*)', user, re.S)
    q=qm.group(1).strip() if qm else ''
    opts=parse_options(q)
    if opts:
        opt_records.append((r,q,opts))
        # category
        cm=re.search(r'Category:\s*(.+)', user)
        cat_counter[cm.group(1).strip() if cm else 'NONE']+=1
print('records with A-D options:',len(opt_records))
print('categories:',cat_counter)
# answer parse
ans_labels=collections.Counter()
for r,q,opts in opt_records:
    a=r['messages'][1]['content']
    am=re.search(r'Answer:\s*(.+)', a)
    ans=am.group(1).strip() if am else ''
    # label?
    lm=re.match(r'^([A-D])\)', ans)
    if lm: ans_labels[lm.group(1)]+=1
    else: ans_labels['NO_LABEL']+=1
print('answer label counts',ans_labels)
# show non-label answers samples
nolabel=[ (r['messages'][1]['content']) for r,q,opts in opt_records if not re.match(r'^[A-D]\)', re.search(r'Answer:\s*(.+)', r['messages'][1]['content']).group(1).strip())]
print('nonlabel count',len(nolabel))
print(nolabel[:10])