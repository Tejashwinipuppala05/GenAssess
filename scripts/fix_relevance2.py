p='src/rounds/routes.py'
s=open(p).read()
old='''    relevant = [a for a in topic_candidates if _word_overlap(correct, a) >= 0.05]
    if len(relevant) >= 3:
        candidates = relevant
    elif len(topic_candidates) >= 3:
        candidates = topic_candidates
    else:
        candidates = []'''
new='''    relevant = [a for a in topic_candidates if _word_overlap(correct, a) >= 0.05]
    if len(relevant) >= 3:
        candidates = relevant
    else:
        return None'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')