import json, re
base='data/datasets'
apt=json.load(open(base+'/aptitude.json',encoding='utf-8'))
for r in apt:
    user=r['messages'][0]['content']
    if 'Jumbled' in user:
        print(user)
        print('---')
        print(r['messages'][1]['content'])
        print('===')
        break