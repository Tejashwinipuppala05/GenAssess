p='src/question_banks/technical.py'
s=open(p).read()
old='''if _FAQGURU_TECHNICAL_PATH.exists():
    for _record in json.loads(_FAQGURU_TECHNICAL_PATH.read_text(encoding="utf-8")):
        TECHNICAL_QUESTIONS.append(_record)'''
new='''if _FAQGURU_TECHNICAL_PATH.exists():
    _seen_questions = {question["question"].strip().lower() for question in TECHNICAL_QUESTIONS}
    for _record in json.loads(_FAQGURU_TECHNICAL_PATH.read_text(encoding="utf-8")):
        _normalized = _record["question"].strip().lower()
        if _normalized in _seen_questions:
            continue
        _seen_questions.add(_normalized)
        TECHNICAL_QUESTIONS.append(_record)'''
assert old in s
s=s.replace(old,new,1)
open(p,'w').write(s)
print('done')