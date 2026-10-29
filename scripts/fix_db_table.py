p='src/auth/database.py'
s=open(p).read()
# remove misplaced block
block='''                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL REFERENCES job_posts(id) ON DELETE CASCADE,
                    candidate_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    status TEXT NOT NULL DEFAULT 'APPLIED'
                        CHECK (status IN ('APPLIED', 'REVIEWED', 'SHORTLISTED', 'REJECTED')),
                    score INTEGER,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(job_id, candidate_id)
                );
                CREATE INDEX IF NOT EXISTS job_applications_job_idx ON job_applications(job_id);
                CREATE INDEX IF NOT EXISTS job_applications_candidate_idx ON job_applications(candidate_id);

'''
s=s.replace(block,'')
# insert before closing of executescript string: after aptitude index line
needle='''                CREATE INDEX IF NOT EXISTS aptitude_answers_question_history_idx
                    ON aptitude_practice_answers(question_id, is_correct);
'''
addition=needle+'''
                CREATE TABLE IF NOT EXISTS job_applications (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    job_id INTEGER NOT NULL REFERENCES job_posts(id) ON DELETE CASCADE,
                    candidate_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    status TEXT NOT NULL DEFAULT 'APPLIED'
                        CHECK (status IN ('APPLIED', 'REVIEWED', 'SHORTLISTED', 'REJECTED')),
                    score INTEGER,
                    notes TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    UNIQUE(job_id, candidate_id)
                );
                CREATE INDEX IF NOT EXISTS job_applications_job_idx ON job_applications(job_id);
                CREATE INDEX IF NOT EXISTS job_applications_candidate_idx ON job_applications(candidate_id);
'''
s=s.replace(needle,addition,1)
open(p,'w').write(s)
print('done')