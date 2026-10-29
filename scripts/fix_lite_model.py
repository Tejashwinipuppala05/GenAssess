p='scripts/test_gemini_lite.py'
s=open(p).read()
s=s.replace("os.environ['OPENAI_MODEL'] = 'gemini-2.5-flash-lite'","os.environ['OPENAI_MODEL'] = 'gemini-3.5-flash-lite'")
open(p,'w').write(s)
print('done')