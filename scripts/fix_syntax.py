p='src/rounds/routes.py'
s=open(p).read()
bad='''    # If no MCQ options are available, fall back to descriptive evaluation.
    question = Question(
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
good='''    # If no MCQ options are available, fall back to descriptive evaluation.
    question = Question('''
assert bad in s
s=s.replace(bad,good,1)
open(p,'w').write(s)
print('done')