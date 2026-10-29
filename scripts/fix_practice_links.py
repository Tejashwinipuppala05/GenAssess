p='frontend/src/app/candidate/practice/page.tsx'
s=open(p).read()
addition='''      <div className="mt-4 flex flex-wrap gap-3">
        <Link className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700" href="/candidate/practice/technical">Technical concepts</Link>
        <Link className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700" href="/candidate/practice/coding">Coding challenge</Link>
        <Link className="rounded-lg bg-slate-100 px-3 py-2 text-xs font-bold text-slate-700 hover:bg-indigo-50 hover:text-indigo-700" href="/candidate/practice/behavioral">Behavioral interview</Link>
      </div>
'''
s=s.replace('    </DashboardFrame>', addition+'    </DashboardFrame>', 1)
open(p,'w').write(s)
print('done')