p='src/rounds/routes.py'
s=open(p).read()
# remove decorator above _role_tokens
s=s.replace('''@router.get("/{round_name}/questions", response_model=list[RoundQuestion])
def _role_tokens(target_role: str) -> set[str]:''','''def _role_tokens(target_role: str) -> set[str]:''')
# ensure list_questions has decorator
s=s.replace('def list_questions(\n    round_name: str,','''@router.get("/{round_name}/questions", response_model=list[RoundQuestion])
def list_questions(
    round_name: str,''',1)
open(p,'w').write(s)
print('done')