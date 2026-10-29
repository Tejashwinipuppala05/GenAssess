p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('relevant = [a for a in topic_candidates if _word_overlap(correct, a) >= 0.05]',
            'relevant = [a for a in topic_candidates if _word_overlap(correct, a) >= 0.15]')
open(p,'w').write(s)
print('done')