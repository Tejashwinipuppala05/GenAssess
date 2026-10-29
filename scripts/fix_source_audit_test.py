p='tests/test_question_banks.py'
s=open(p).read()
s=s.replace('assert SOURCE_AUDIT["aptitude"]["imported_rows"] == 0','assert SOURCE_AUDIT["aptitude"]["imported_rows"] == 150')
open(p,'w').write(s)
print('done')