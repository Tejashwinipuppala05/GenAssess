p='tests/test_aptitude.py'
s=open(p).read()
s=s.replace('assert bank_questions[selected_id] == "Old wording"','assert bank_questions[next(iter(selected_ids))] == "Old wording"')
open(p,'w').write(s)
print('done')