p='frontend/src/app/candidate/practice/behavioral/page.tsx'
s=open(p).read()
s=s.replace('questions.map((q) => (','questions.map((q, index) => (')
s=s.replace('<p className="mb-2 font-semibold">{q.question}</p>','<p className="mb-1 text-xs font-bold text-indigo-600">Question {index + 1}</p>\n            <p className="mb-2 font-semibold">{q.question}</p>')
open(p,'w').write(s)
print('done')