p='scripts/test_gemini.py'
s=open(p).read()
s=s.replace("os.environ['OPENAI_MODEL'] = 'gemini-2.5-flash'","os.environ['OPENAI_MODEL'] = 'gemini-3.8-flash'")
open(p,'w').write(s)
print('done')