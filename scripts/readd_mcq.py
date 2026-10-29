p='src/rounds/routes.py'
s=open(p).read()
old='''    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))
    result = []'''
new='''    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))

    if round_name == "technical":
        for question in chosen:
            qid = question["id"]
            if qid in _TECHNICAL_OPTIONS_CACHE:
                options = _TECHNICAL_OPTIONS_CACHE[qid]
            else:
                correct = _truncate_option(question["correct_answer"])
                distractors = _llm_distractors(question)
                if distractors is None:
                    distractors = _similar_distractors(question, bank)
                options = distractors + [correct]
                rng.shuffle(options)
                _TECHNICAL_OPTIONS_CACHE[qid] = options
            _TECHNICAL_OPTION_ANSWERS[qid] = options.index(_truncate_option(question["correct_answer"]))
            question["_options"] = options
    result = []'''
assert old in s
s=s.replace(old,new,1)
# add options field in RoundQuestion construction
s=s.replace('''                license=question["license"],
                test_cases=question.get("test_cases"),''','''                license=question["license"],
                options=question.get("_options"),
                test_cases=question.get("test_cases"),''')
open(p,'w').write(s)
print('done')