p='tests/test_aptitude.py'
s=open(p).read()
s=s.replace("        (selected_id, unused_question[\"id\"]),","        (next(iter(selected_ids)), unused_question[\"id\"]),")
open(p,'w').write(s)
print('done')