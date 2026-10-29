p='src/rounds/routes.py'
s=open(p).read()
old='''                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("Using heuristic distractors for %s (LLM unavailable/invalid).", question["id"])
                    distractors = _similar_distractors(question, bank)'''
new='''                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("No LLM distractors available for %s; marking as descriptive.", question["id"])
                    question["_options"] = None
                    continue'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')