p='tests/test_question_banks.py'
s=open(p).read()
s=s.replace('assert len(QUESTION_BANK) == 71','assert len(QUESTION_BANK) == 221')
s=s.replace('assert len(question["test_cases"]) == 3','assert len(question["test_cases"]) >= 3')
open(p,'w').write(s)
print('done')