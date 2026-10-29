p='src/rounds/routes.py'
s=open(p).read()
old='''    if round_name == "technical":
        all_answers = [q["correct_answer"] for q in bank]
        for question in chosen:
            correct = question["correct_answer"]
            same_category = [
                q["correct_answer"]
                for q in bank
                if q["category"] == question["category"] and q["correct_answer"] != correct
            ]
            pool = same_category if len(same_category) >= 3 else [a for a in all_answers if a != correct]
            distractors = rng.sample(pool, min(3, len(pool)))
            options = distractors + [correct]
            rng.shuffle(options)
            _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(correct)
            question["_options"] = options'''
new='''    if round_name == "technical":
        all_answers = [q["correct_answer"] for q in bank]
        for question in chosen:
            qid = question["id"]
            if qid in _TECHNICAL_OPTIONS_CACHE:
                options = _TECHNICAL_OPTIONS_CACHE[qid]
            else:
                correct = _truncate_option(question["correct_answer"])
                distractors = _llm_distractors(question)
                if distractors is None:
                    same_category = [
                        _truncate_option(q["correct_answer"])
                        for q in bank
                        if q["category"] == question["category"] and q["correct_answer"] != question["correct_answer"]
                    ]
                    pool = same_category if len(same_category) >= 3 else [_truncate_option(a) for a in all_answers if a != question["correct_answer"]]
                    distractors = rng.sample(pool, min(3, len(pool)))
                options = distractors + [correct]
                rng.shuffle(options)
                _TECHNICAL_OPTIONS_CACHE[qid] = options
            correct_index = options.index(_truncate_option(question["correct_answer"]))
            _TECHNICAL_OPTION_ANSWERS[qid] = correct_index
            question["_options"] = options'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')