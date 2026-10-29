p='src/rounds/routes.py'
s=open(p).read()
old='''                distractors = _llm_distractors(question)
                if distractors is None:
                    # No valid options available without LLM; mark as descriptive.
                    question["_options"] = None
                    continue'''
new='''                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("Using heuristic distractors for %s (LLM unavailable/invalid).", question["id"])
                    distractors = _similar_distractors(question, bank)'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')