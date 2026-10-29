p='src/rounds/routes.py'
s=open(p).read()
s=s.replace('@router.get("/{round_name}/questions", response_model=list[RoundQuestion])\n\ndef _truncate_option','def _truncate_option',1)
open(p,'w').write(s)
print('done')