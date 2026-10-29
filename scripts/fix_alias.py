p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('    target_role: str = Query(default="Software Engineer", alias="targetRole"),','    targetRole: str = Query(default="Software Engineer"),')
# update references inside list_questions
s=s.replace('filtered = [q for q in bank if _technical_relevant(q, target_role)]','filtered = [q for q in bank if _technical_relevant(q, targetRole)]')
s=s.replace('filtered = [q for q in bank if _coding_relevant(q, target_role)]','filtered = [q for q in bank if _coding_relevant(q, targetRole)]')
open(p,'w').write(s)
print('done')