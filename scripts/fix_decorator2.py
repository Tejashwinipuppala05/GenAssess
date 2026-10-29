p='src/rounds/routes.py'
s=open(p).read()
# remove decorator above _truncate_option
s=s.replace('@router.get("/{round_name}/questions", response_model=list[RoundQuestion])\n\ndef _truncate_option', 'def _truncate_option', 1)
# add decorator to list_questions
s=s.replace('def list_questions(\n    round_name: str,', '@router.get("/{round_name}/questions", response_model=list[RoundQuestion])\ndef list_questions(\n    round_name: str,', 1)
open(p,'w').write(s)
print('done')