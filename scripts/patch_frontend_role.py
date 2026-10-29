for p in ['frontend/src/app/candidate/practice/technical/page.tsx','frontend/src/app/candidate/practice/coding/page.tsx','frontend/src/app/candidate/practice/behavioral/page.tsx']:
    s=open(p).read()
    # add targetRole state after first useState? Insert before loading state
    s=s.replace('const [loading, setLoading] = useState(false);','const [targetRole, setTargetRole] = useState("Software Engineer");\n  const [loading, setLoading] = useState(false);')
    # add select UI before button? Insert before load button
    # technical/coding/behavioral all have "Load Questions/Problems"
    s=s.replace('<button onClick={loadQuestions}','''<div className="mb-4">
        <label className="mr-2 text-sm font-semibold">Target role:</label>
        <select value={targetRole} onChange={(e) => setTargetRole(e.target.value)} className="rounded border border-slate-300 px-2 py-1 text-sm">
          <option>Software Engineer</option>
          <option>Data Analyst</option>
          <option>AI Engineer</option>
        </select>
      </div>
      <button onClick={loadQuestions}''')
    # update fetch URL to include targetRole
    s=s.replace('rounds/technical/questions?limit=5','rounds/technical/questions?limit=5&targetRole=' + '${encodeURIComponent(targetRole)}')
    s=s.replace('rounds/coding/questions?limit=5','rounds/coding/questions?limit=5&targetRole=' + '${encodeURIComponent(targetRole)}')
    s=s.replace('rounds/behavioral/questions?limit=3','rounds/behavioral/questions?limit=3&targetRole=' + '${encodeURIComponent(targetRole)}')
    open(p,'w').write(s)
    print(p,'done')