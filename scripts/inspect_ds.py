import urllib.request, json
for ds in ['Prathamesh25/aptitude-qa-dataset','remomo/software-interview-questions','google-research-datasets/mbpp']:
    url=f'https://datasets-server.huggingface.co/info?dataset={ds}'
    print('===',ds)
    try:
        data=json.load(urllib.request.urlopen(url,timeout=60))
        print(json.dumps(data,indent=2)[:4000])
    except Exception as e:
        print('ERR',repr(e))
