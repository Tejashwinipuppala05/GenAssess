p='src/rounds/routes.py'
s=open(p).read()
old='''    question_data = _find("technical", payload.question_id)
    if payload.selected_answer is not None:
        correct_index = _TECHNICAL_OPTION_ANSWERS.get(payload.question_id)
        if correct_index is None:
            all_answers = [q["correct_answer"] for q in TECHNICAL_QUESTIONS]
            correct = _truncate_option(question_data["correct_answer"])
            distractors = _llm_distractors(question_data)
            if distractors is None:
                return None
            options = distractors + [correct]
            rng = random.SystemRandom()
            rng.shuffle(options)
            options.append("I don't know")
            _TECHNICAL_OPTIONS_CACHE[payload.question_id] = options
            correct_index = options.index(correct)
            _TECHNICAL_OPTION_ANSWERS[payload.question_id] = correct_index'''
new='''    question_data = _find("technical", payload.question_id)
    if payload.selected_answer is not None and payload.question_id in _TECHNICAL_OPTION_ANSWERS:
        correct_index = _TECHNICAL_OPTION_ANSWERS[payload.question_id]
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
    # If no MCQ options are available, fall back to descriptive evaluation.
    question = Question('''
assert old in s
s=s.replace(old,new,1)
# Now remove the duplicate question = Question( that follows? There is already one after.
s=s.replace('''    question = Question(
        prompt=question_data["question"],''','''    question = Question(
        prompt=question_data["question"],''',1)
open(p,'w').write(s)
print('done')