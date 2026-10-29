p='tests/test_question_banks.py'
s=open(p).read()
for old in ['"Introduction": 5,','"Teamwork": 5,','"Leadership": 5,','"Conflict Resolution": 5,','"Problem Solving": 5,','"Communication": 5,','"Adaptability": 5,','"Failure/Learning": 5,','"Workplace Situations": 5,','"Role-Specific Situations": 5,']:
    s=s.replace(old, old.replace(': 5,',': 7,'))
open(p,'w').write(s)
print('done')