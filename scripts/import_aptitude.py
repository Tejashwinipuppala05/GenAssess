import json, re, os
base='data/datasets'
apt=json.load(open(base+'/aptitude.json',encoding='utf-8'))
out=[]
counter=collections_counter if False else None
import collections
idx_by_topic=collections.defaultdict(int)
def parse_options(q):
    matches=list(re.finditer(r'(?<!\w)([A-D])\)\s*(.*?)(?=(?<!\w)[A-D]\)|$)', q, re.S))
    labels=[m.group(1) for m in matches]
    if labels==['A','B','C','D']:
        return [m.group(2).strip() for m in matches]
    return None
def level_to_diff(level):
    return {'01 Basic':'Easy','02 Intermediate':'Medium','03 Advance':'Hard'}.get(level.strip(),'Medium')
rejected=0
for r in apt:
    user=r['messages'][0]['content']
    ans_text=r['messages'][1]['content']
    sm=re.search(r'Subject:\s*(.+)', user); subject=sm.group(1).strip() if sm else ''
    lm=re.search(r'Level:\s*(.+)', user); level=lm.group(1).strip() if lm else ''
    cm=re.search(r'Category:\s*(.+)', user); category=cm.group(1).strip() if cm else ''
    qm=re.search(r'Question:\s*(.*)', user, re.S); q=(qm.group(1).strip() if qm else '')
    # remove options from question text? keep full question; options parsed
    opts=parse_options(q)
    am=re.search(r'Answer:\s*(.+)', ans_text); answer=am.group(1).strip() if am else ''
    # single label?
    label_match=re.match(r'^([A-D])\)', answer)
    if not opts or not label_match:
        rejected+=1
        continue
    # exclude jumbled? jumbled answer is permutation; already label_match? jumbled answer like "C-D-A-B" doesn't match ^[A-D]\) because has hyphen? Actually regex ^([A-D])\) requires closing paren; "C-D-A-B" no. So excluded.
    label=label_match.group(1)
    correct_index=ord(label)-ord('A')
    # explanation: solution text before Answer
    em=re.search(r'Solution:\s*(.*?)(?:Answer:|$)', ans_text, re.S)
    explanation=em.group(1).strip() if em else ''
    # topic from category (strip trailing (..))
    topic=category.split('(')[0].strip()
    # clean question text by removing option labels? Keep original question text (includes options). 
    # But for MCQ, question stem should include options? Existing aptitude questions have question text without options. 
    # Remove trailing options from stem:
    stem=q
    # cut at first "A)" option
    stem=re.split(r'(?<!\w)A\)', stem, maxsplit=1)[0].strip()
    # remove **Options** marker
    stem=stem.replace('**Options**','').strip()
    # difficulty
    difficulty=level_to_diff(level)
    idx_by_topic[topic]+=1
    rec={
        "id": f"aptqa-{topic.lower().replace(' ','-').replace('/','-')}-{idx_by_topic[topic]:03d}",
        "question": stem if stem else q,
        "options": opts,
        "correct_answer": correct_index,
        "explanation": explanation,
        "topic": topic,
        "subtopic": topic,
        "category": "Verbal Ability",
        "difficulty": difficulty,
        "estimated_time_seconds": 75,
        "source_type": "Aptitude-QA (Prathamesh25/aptitude-qa-dataset)",
        "tags": ["aptitude-qa", topic.lower(), level.lower().replace(' ','-')],
        "target_roles": [],
        "source": "Aptitude-QA dataset",
        "license": "Apache-2.0",
        "attribution": "Prathamesh25/aptitude-qa-dataset (Hugging Face), imported and validated by GenAssess.",
    }
    out.append(rec)
os.makedirs('data/question_banks',exist_ok=True)
json.dump(out, open('data/question_banks/aptitude_imported.json','w',encoding='utf-8'), ensure_ascii=False, indent=2)
print('imported',len(out),'rejected',rejected)