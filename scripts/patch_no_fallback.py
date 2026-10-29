p='src/rounds/routes.py'
s=open(p).read()

# In list_questions technical branch, remove fallback to similar distractors
old='''                distractors = _llm_distractors(question)
                if distractors is None:
                    distractors = _similar_distractors(question, bank)
                options = distractors + [correct]
                rng.shuffle(options)
                _TECHNICAL_OPTIONS_CACHE[qid] = options'''
new='''                distractors = _llm_distractors(question)
                if distractors is None:
                    # No valid options available without LLM; mark as descriptive.
                    question["_options"] = None
                    continue
                options = distractors + [correct]
                rng.shuffle(options)
                options.append("I don't know")
                _TECHNICAL_OPTIONS_CACHE[qid] = options'''
assert old in s
s=s.replace(old,new,1)

# Update cache assignment and index
old2='''            _TECHNICAL_OPTION_ANSWERS[qid] = options.index(_truncate_option(question["correct_answer"]))'''
new2='''            _TECHNICAL_OPTION_ANSWERS[qid] = options.index(_truncate_option(question["correct_answer"]))'''
# options may be None; guard
s=s.replace('''            _TECHNICAL_OPTION_ANSWERS[qid] = options.index(_truncate_option(question["correct_answer"]))''',
            '''            if options is not None:
                _TECHNICAL_OPTION_ANSWERS[qid] = options.index(_truncate_option(question["correct_answer"]))''',1)

# In evaluate_technical regeneration, remove fallback
old3='''            distractors = _llm_distractors(question_data)
            if distractors is None:
                distractors = _similar_distractors(question_data, TECHNICAL_QUESTIONS)
            options = distractors + [correct]
            _TECHNICAL_OPTIONS_CACHE[payload.question_id] = options'''
new3='''            distractors = _llm_distractors(question_data)
            if distractors is None:
                return None
            options = distractors + [correct]
            rng = random.SystemRandom()
            rng.shuffle(options)
            options.append("I don't know")
            _TECHNICAL_OPTIONS_CACHE[payload.question_id] = options'''
# But evaluate_technical doesn't have rng; replace carefully
s=s.replace(old3,new3,1)

open(p,'w').write(s)
print('done')