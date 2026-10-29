p='src/rounds/routes.py'
s=open(p).read()
old='''    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))'''
new='''    rng = random.SystemRandom()
    chosen = rng.sample(filtered, min(limit, len(filtered)))

    if round_name == "technical":
        all_answers = [q["correct_answer"] for q in bank]
        for question in chosen:
            correct = question["correct_answer"]
            distractors = rng.sample([a for a in all_answers if a != correct], min(3, len(all_answers) - 1))
            options = distractors + [correct]
            rng.shuffle(options)
            _TECHNICAL_OPTION_ANSWERS[question["id"]] = options.index(correct)
            question["_options"] = options'''
assert old in s
s=s.replace(old,new,1)
# Update RoundQuestion construction to include options
s=s.replace(
'''                test_cases=question.get("test_cases"),
                follow_up_dimensions=question.get("follow_up_dimensions"),''',
'''                options=question.get("_options"),
                test_cases=question.get("test_cases"),
                follow_up_dimensions=question.get("follow_up_dimensions"),''')
open(p,'w').write(s)
print('done')