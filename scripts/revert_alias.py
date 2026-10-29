p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('    targetRole: str = Query(default="Software Engineer"),','    target_role: str = Query(default="Software Engineer"),')
s=s.replace('filtered = [q for q in bank if _technical_relevant(q, targetRole)]','filtered = [q for q in bank if _technical_relevant(q, target_role)]')
s=s.replace('filtered = [q for q in bank if _coding_relevant(q, targetRole)]','filtered = [q for q in bank if _coding_relevant(q, target_role)]')
open(p,'w').write(s)
print('done')