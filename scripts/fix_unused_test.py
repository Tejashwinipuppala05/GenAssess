p='tests/test_aptitude.py'
s=open(p).read()
old='''    selected_id = session["questions"][0]["id"]
    unused_question = next(question for question in QUESTION_BANK if question["id"] != selected_id)'''
new='''    selected_ids = {question["id"] for question in session["questions"]}
    unused_question = next(question for question in QUESTION_BANK if question["id"] not in selected_ids)'''
s=s.replace(old,new)
open(p,'w').write(s)
print('done')