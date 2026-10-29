p='src/rounds/routes.py'
s=open(p).read()

# Remove MCQ generation block in list_questions
old='''    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))

    if round_name == "technical":
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
new='''    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))'''
assert old in s
s=s.replace(old,new,1)

# Remove options from RoundQuestion construction
s=s.replace('''                options=question.get("_options"),
                test_cases=question.get("test_cases"),''','''                test_cases=question.get("test_cases"),''')

# Simplify evaluate_technical: remove selected_answer MCQ branch
old_eval='''    question_data = _find("technical", payload.question_id)
    if payload.selected_answer is not None:
        correct_index = _TECHNICAL_OPTION_ANSWERS.get(payload.question_id)
        if correct_index is None:
            all_answers = [q["correct_answer"] for q in TECHNICAL_QUESTIONS]
            correct = _truncate_option(question_data["correct_answer"])
            same_category = [
                _truncate_option(q["correct_answer"])
                for q in TECHNICAL_QUESTIONS
                if q["category"] == question_data["category"] and q["correct_answer"] != question_data["correct_answer"]
            ]
            pool = same_category if len(same_category) >= 3 else [_truncate_option(a) for a in all_answers if a != question_data["correct_answer"]]
            distractors = random.sample(pool, min(3, len(pool)))
            options = distractors + [correct]
            _TECHNICAL_OPTIONS_CACHE[payload.question_id] = options
            correct_index = options.index(correct)
            _TECHNICAL_OPTION_ANSWERS[payload.question_id] = correct_index
        is_correct = payload.selected_answer == correct_index
        score = 100 if is_correct else 0
        return EvaluateResponse(
            question_id=payload.question_id,
            score=score,
            method="Multiple-choice",
            correctness="Correct" if is_correct else "Incorrect",
            strengths=["Selected the correct option."] if is_correct else [],
            missing_concepts=[] if is_correct else ["Review the selected concept."],
            suggestions=[] if is_correct else ["Try again and review the topic."],
        )
    question = Question('''
new_eval='''    question_data = _find("technical", payload.question_id)
    question = Question('''
assert old_eval in s
s=s.replace(old_eval,new_eval,1)

open(p,'w').write(s)
print('done')