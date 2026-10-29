import json, re, collections
base='data/datasets'
apt=json.load(open(base+'/aptitude.json',encoding='utf-8'))
# find records with option-like labels in user or answer
count_opt=0
examples=[]
for r in apt:
    user=r['messages'][0]['content']
    ans=r['messages'][1]['content']
    if re.search(r'\b[A-D]\)', user) or re.search(r'\b[A-D]\)', ans):
        count_opt+=1
        if len(examples)<5:
            examples.append((user,ans))
print('option-label records',count_opt)
for u,a in examples:
    print('---USER---',u)
    print('---ANS---',a)
# inspect one record full
print('=== sample 0 ===')
print(apt[0]['messages'][0]['content'])
print('---')
print(apt[0]['messages'][1]['content'])