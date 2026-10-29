p='frontend/src/app/candidate/practice/technical/page.tsx'
s=open(p).read()
# add selectedAnswers state
s=s.replace('const [answers, setAnswers] = useState<Record<string, string>>({});',
            'const [selectedAnswers, setSelectedAnswers] = useState<Record<string, number | null>>({});')
# replace textarea+submit with options
old='''            <textarea
              className="w-full rounded border border-slate-300 p-2"
              rows={4}
              value={answers[q.id] || ""}
              onChange={(e) => setAnswers((prev) => ({ ...prev, [q.id]: e.target.value }))}
            />
            <button
              onClick={() => submit(q.id)}
              className="mt-2 rounded bg-slate-800 px-3 py-1 text-white"
            >
              Submit
            </button>'''
new='''            <div className="space-y-2">
              {(q.options || []).map((opt, idx) => (
                <label key={idx} className="flex items-center gap-2 rounded border border-slate-200 p-2">
                  <input
                    type="radio"
                    name={q.id}
                    checked={selectedAnswers[q.id] === idx}
                    onChange={() => setSelectedAnswers((prev) => ({ ...prev, [q.id]: idx }))}
                  />
                  <span>{opt}</span>
                </label>
              ))}
            </div>
            <button
              onClick={() => submit(q.id)}
              className="mt-2 rounded bg-slate-800 px-3 py-1 text-white"
            >
              Submit
            </button>'''
assert old in s
s=s.replace(old,new)
# update submit function to send selectedAnswer
s=s.replace(
'''    const res = await fetch(`${API_BASE}/candidate/practice/rounds/technical/evaluate`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionId, answer: answers[questionId] || "" }),
    });''',
'''    const res = await fetch(`${API_BASE}/candidate/practice/rounds/technical/evaluate`, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ questionId, answer: "", selectedAnswer: selectedAnswers[questionId] }),
    });''')
# update Question type to include options
s=s.replace('  difficulty: string;\n};','  difficulty: string;\n  options?: string[];\n};')
open(p,'w').write(s)
print('done')