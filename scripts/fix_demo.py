p='scripts/run_interview_demo.py'
s=open(p).read()
s=s.replace('print(f"Feedback: {result.feedback}")','print(f"Suggestions: {result.suggestions}")')
open(p,'w').write(s)
print('done')