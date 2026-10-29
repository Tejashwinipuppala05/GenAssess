import urllib.request, json, os
BASE='C:/Users/tejas/GenAssess/data/datasets'
os.makedirs(BASE,exist_ok=True)
specs=[
 ('aptitude','Prathamesh25/aptitude-qa-dataset','default','train'),
 ('software_interview','remomo/software-interview-questions','default','train'),
]
for name,ds,config,split in specs:
    print('fetching',name)
    allrows=[]
    offset=0
    length=100
    while True:
        url=f'https://datasets-server.huggingface.co/rows?dataset={ds}&config={config}&split={split}&offset={offset}&length={length}'
        data=json.load(urllib.request.urlopen(url,timeout=120))
        rows=[r['row'] for r in data['rows']]
        allrows.extend(rows)
        if len(rows)<length: break
        offset+=length
    with open(os.path.join(BASE,name+'.json'),'w',encoding='utf-8') as f:
        json.dump(allrows,f,ensure_ascii=False,indent=2)
    print(name,len(allrows))
# MBPP sanitized train already known; fetch
name='mbpp_sanitized_train'
ds='google-research-datasets/mbpp'; config='sanitized'; split='train'
allrows=[]
offset=0; length=100
while True:
    url=f'https://datasets-server.huggingface.co/rows?dataset={ds}&config={config}&split={split}&offset={offset}&length={length}'
    data=json.load(urllib.request.urlopen(url,timeout=120))
    rows=[r['row'] for r in data['rows']]
    allrows.extend(rows)
    if len(rows)<length: break
    offset+=length
with open(os.path.join(BASE,name+'.json'),'w',encoding='utf-8') as f:
    json.dump(allrows,f,ensure_ascii=False,indent=2)
print(name,len(allrows))