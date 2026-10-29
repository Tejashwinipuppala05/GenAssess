import json
rows=json.load(open('data/question_banks/faqguru_technical.json',encoding='utf-8'))
changed=0
for r in rows:
    old=r['difficulty']
    ans=r['correct_answer']
    q=r['question']
    if '```' in ans or len(ans)>700:
        new='Hard'
    elif len(ans)<250 and len(q)<120:
        new='Easy'
    else:
        new='Medium'
    if new!=old:
        changed+=1
    r['difficulty']=new
json.dump(rows, open('data/question_banks/faqguru_technical.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
from collections import Counter
print('changed:',changed)
print(Counter(r['difficulty'] for r in rows))