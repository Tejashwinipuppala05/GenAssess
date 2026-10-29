from src.question_banks import CODING_QUESTIONS, execute_python_test_cases
bad=[]
for q in CODING_QUESTIONS:
    r=execute_python_test_cases(q['reference_solution'], q['test_cases'], test_imports=q.get('test_imports',[]))
    if not r['passed']:
        bad.append((q['id'], r['stderr'][:200]))
print('total',len(CODING_QUESTIONS),'bad',len(bad))
print(bad[:5])