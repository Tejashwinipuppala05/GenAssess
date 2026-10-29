import urllib.request, json
def rows(ds, config, split, offset=0, length=5):
    url=f'https://datasets-server.huggingface.co/rows?dataset={ds}&config={config}&split={split}&offset={offset}&length={length}'
    data=json.load(urllib.request.urlopen(url,timeout=60))
    return data['rows']
for ds,config,split in [('Prathamesh25/aptitude-qa-dataset','default','train'),('remomo/software-interview-questions','default','train'),('google-research-datasets/mbpp','sanitized','train')]:
    print('===',ds)
    r=rows(ds,config,split,0,3)
    print(json.dumps(r,indent=2)[:5000])
