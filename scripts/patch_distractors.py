p='src/rounds/routes.py'
s=open(p).read()
old='''            correct = question["correct_answer"]
            distractors = rng.sample([a for a in all_answers if a != correct], min(3, len(all_answers) - 1))
            options = distractors + [correct]'''
new='''            correct = question["correct_answer"]
            same_category = [
                q["correct_answer"]
                for q in bank
                if q["category"] == question["category"] and q["correct_answer"] != correct
            ]
            pool = same_category if len(same_category) >= 3 else [a for a in all_answers if a != correct]
            distractors = rng.sample(pool, min(3, len(pool)))
            options = distractors + [correct]'''
assert old in s
s=s.replace(old,new,1)
# also update regeneration block in evaluate_technical
old2='''            all_answers = [q["correct_answer"] for q in TECHNICAL_QUESTIONS]
            correct = question_data["correct_answer"]
            distractors = random.sample([a for a in all_answers if a != correct], min(3, len(all_answers) - 1))
            options = distractors + [correct]'''
new2='''            all_answers = [q["correct_answer"] for q in TECHNICAL_QUESTIONS]
            correct = question_data["correct_answer"]
            same_category = [
                q["correct_answer"]
                for q in TECHNICAL_QUESTIONS
                if q["category"] == question_data["category"] and q["correct_answer"] != correct
            ]
            pool = same_category if len(same_category) >= 3 else [a for a in all_answers if a != correct]
            distractors = random.sample(pool, min(3, len(pool)))
            options = distractors + [correct]'''
assert old2 in s
s=s.replace(old2,new2,1)
open(p,'w').write(s)
print('done')