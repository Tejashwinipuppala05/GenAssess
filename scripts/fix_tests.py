p='tests/test_question_banks.py'
s=open(p).read()
s=s.replace('"aptitude": 71,','"aptitude": 221,')
s=s.replace('"coding": 5,','"coding": 120,')
s=s.replace('"behavioral": 50,','"behavioral": 70,')
s=s.replace('assert len(CODING_QUESTIONS) == 5','assert len(CODING_QUESTIONS) == 120')
s=s.replace('assert len(BEHAVIORAL_QUESTIONS) == 50','assert len(BEHAVIORAL_QUESTIONS) == 70')
open(p,'w').write(s)
print('done')