p='src/rounds/routes.py'
s=open(p).read()
old='''    question_data = _find("technical", payload.question_id)
    question = Question(
        prompt=question_data["question"],'''
new='''    question_data = _find("technical", payload.question_id)
    if payload.selected_answer is not None:
        correct_index = _TECHNICAL_OPTION_ANSWERS.get(payload.question_id)
        if correct_index is None:
            all_answers = [q["correct_answer"] for q in TECHNICAL_QUESTIONS]
            correct = question_data["correct_answer"]
            distractors = random.sample([a for a in all_answers if a != correct], min(3, len(all_answers) - 1))
            options = distractors + [correct]
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
    question = Question(
        prompt=question_data["question"],'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')