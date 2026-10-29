p='src/rounds/routes.py'
s=open(p).read()
old='''                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("Using heuristic distractors for %s (LLM unavailable/invalid).", question["id"])
                    distractors = _similar_distractors(question, bank)
                options = distractors + [correct]
                rng.shuffle(options)
                options.append("I don't know")
                _TECHNICAL_OPTIONS_CACHE[qid] = options'''
new='''                distractors = _llm_distractors(question)
                if distractors is None:
                    logger.info("Using heuristic distractors for %s (LLM unavailable/invalid).", question["id"])
                    distractors = _similar_distractors(question, bank)
                if distractors is None:
                    logger.info("No relevant distractors for %s; marking as descriptive.", question["id"])
                    question["_options"] = None
                    continue
                options = distractors + [correct]
                rng.shuffle(options)
                options.append("I don't know")
                _TECHNICAL_OPTIONS_CACHE[qid] = options'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')