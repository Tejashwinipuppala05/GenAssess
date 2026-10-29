p='src/rounds/routes.py'
s=open(p).read()
s=s.replace(
'        client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None)',
'        client = OpenAI(api_key=api_key, base_url=os.getenv("OPENAI_BASE_URL") or None, timeout=15.0)')
open(p,'w').write(s)
print('done')