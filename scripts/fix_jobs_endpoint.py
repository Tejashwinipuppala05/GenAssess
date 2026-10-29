p='src/applications/routes.py'
s=open(p).read()
bad='''@candidate_router.get("/jobs", response_model=list[dict])
def list_jobs(connection: Annotated[sqlite3.Connection, Depends(get_database)]) -> list[dict]:
    rows = connection.execute("SELECT id, title, description, location, work_arrangement, created_at FROM job_posts ORDER BY created_at DESC").fetchall()
    return [dict(row) for row in rows]
'''
s=s.replace(bad,'')
# append endpoint at end
s += '''

@candidate_router.get("/jobs", response_model=list[dict])
def list_jobs(connection: Annotated[sqlite3.Connection, Depends(get_database)]) -> list[dict]:
    rows = connection.execute(
        "SELECT id, title, description, location, work_arrangement, created_at FROM job_posts ORDER BY created_at DESC"
    ).fetchall()
    return [dict(row) for row in rows]
'''
open(p,'w').write(s)
print('done')