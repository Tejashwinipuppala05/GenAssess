p='frontend/src/app/candidate/practice/technical/page.tsx'
s=open(p).read()
s=s.replace('href="/candidate/practice" className="text-indigo-700">Adaptive interview','href="/candidate/practice/technical/interview" className="text-indigo-700">Adaptive interview')
open(p,'w').write(s)
print('done')