p='frontend/src/app/candidate/practice/coding/page.tsx'
s=open(p).read()
s=s.replace('limit=3','limit=5')
# add numbered label before question
s=s.replace('<p className="mb-2 font-semibold">{q.question}</p>','<p className="mb-1 text-xs font-bold text-indigo-600">Question {index + 1}</p>\n            <p className="mb-2 font-semibold">{q.question}</p>')
# need map index; update map signature
s=s.replace('questions.map((q) => (','questions.map((q, index) => (')
open(p,'w').write(s)
print('done')