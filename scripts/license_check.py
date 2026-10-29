import urllib.request
for url in ['https://huggingface.co/datasets/remomo/software-interview-questions','https://huggingface.co/datasets/remomo/software-interview-questions/raw/main/README.md']:
    print('===',url)
    try:
        print(urllib.request.urlopen(url,timeout=30).read().decode('utf-8')[:4000])
    except Exception as e:
        print('ERR',e)