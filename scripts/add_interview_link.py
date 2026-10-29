p='frontend/src/app/candidate/practice/technical/page.tsx'
s=open(p).read()
addition='''      <div className="mb-6 rounded-xl border border-indigo-200 bg-indigo-50 p-4">
        <p className="text-sm font-semibold text-indigo-900">Want a full adaptive technical interview?</p>
        <p className="mt-1 text-xs text-indigo-700">Get AI-evaluated answers, difficulty progression, and a final result report.</p>
        <Link href="/candidate/practice/technical/interview" className="mt-3 inline-block rounded bg-indigo-600 px-4 py-2 text-sm font-semibold text-white">
          Start Adaptive Interview
        </Link>
      </div>
'''
s=s.replace('      <h1 className="text-2xl font-bold">Technical Concepts Practice</h1>',
            '      <h1 className="text-2xl font-bold">Technical Concepts Practice</h1>\n' + addition, 1)
open(p,'w').write(s)
print('done')