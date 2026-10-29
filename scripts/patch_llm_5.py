p='src/rounds/routes.py'
s=open(p).read()
old='''        correct_index = _TECHNICAL_OPTION_ANSWERS.get(payload.question_id)
        if correct_index is None:
            all_answers = [q["correct_answer"] for q in TECHNICAL_QUESTIONS]
            correct = question_data["correct_answer"]
            same_category = [
                q["correct_answer"]
                for q in TECHNICAL_QUESTIONS
                if q["category"] == question_data["category"] and q["correct_answer"] != correct
            ]
            pool = same_category if len(same_category) >= 3 else [a for a in all_answers if a != correct]
            distractors = random.sample(pool, min(3, len(pool)))
            options = distractors + [correct]
            correct_index = options.index(correct)
            _TECHNICAL_OPTION_ANSWERS[payload.question_id] = correct_index'''
new='''        correct_index = _TECHNICAL_OPTION_ANSWERS.get(payload.question_id)
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
            _TECHNICAL_OPTION_ANSWERS[payload.question_id] = correct_index'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')