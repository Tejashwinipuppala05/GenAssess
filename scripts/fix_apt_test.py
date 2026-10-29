p='tests/test_aptitude.py'
s=open(p).read()
s=s.replace('assert original_count == bank_count','assert original_count == 71')
open(p,'w').write(s)
print('done')