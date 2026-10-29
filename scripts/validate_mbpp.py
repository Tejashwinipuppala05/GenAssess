import json, subprocess, sys, os, tempfile
base='data/datasets'
rows=json.load(open(base+'/mbpp_sanitized_train.json',encoding='utf-8'))
print('total',len(rows))
existing={602,604,606,608,611}
passing=[]
failing=[]
for r in rows:
    tid=r['task_id']
    if tid in existing:
        continue
    imports='\n'.join(r.get('test_imports') or [])
    code=r['code']
    tests='\n'.join(r['test_list'])
    script=f"{imports}\n{code}\n{tests}\nprint('OK')\n"
    with tempfile.NamedTemporaryFile('w',suffix='.py',delete=False,encoding='utf-8') as f:
        f.write(script); path=f.name
    try:
        res=subprocess.run([sys.executable,path],capture_output=True,text=True,timeout=10)
        if res.returncode==0 and 'OK' in res.stdout:
            passing.append(tid)
        else:
            failing.append((tid,res.returncode,res.stderr[:300]))
    finally:
        os.remove(path)
print('passing',len(passing))
print('failing',len(failing))
print('first passing',passing[:30])
print('failing sample',failing[:10])