import urllib.request, json
for d in ['Danhpham2000/computer_science_qa_dataset','lmms-lab/CSBench_MCQ']:
    print('===',d)
    info=json.load(urllib.request.urlopen('https://datasets-server.huggingface.co/info?dataset='+d,timeout=30))
    print(json.dumps(info['dataset_info'],indent=2)[:2000])