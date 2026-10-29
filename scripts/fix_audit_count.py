p='src/question_banks/source_audit.py'
s=open(p).read()
s=s.replace('"imported_rows": 1599,','"imported_rows": 1593,')
s=s.replace('"filtered_rows": 0,','"filtered_rows": 6,',1)
open(p,'w').write(s)
print('done')