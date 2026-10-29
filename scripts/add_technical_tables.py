p='src/auth/database.py'
s=open(p).read()
needle='''                CREATE INDEX IF NOT EXISTS aptitude_answers_question_history_idx
                    ON aptitude_practice_answers(question_id, is_correct);
'''
addition=needle+'''
                CREATE TABLE IF NOT EXISTS technical_interview_sessions (
                    id TEXT PRIMARY KEY,
                    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    target_role TEXT NOT NULL,
                    experience_level TEXT NOT NULL,
                    topic TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'IN_PROGRESS'
                        CHECK (status IN ('IN_PROGRESS', 'COMPLETED')),
                    total_questions INTEGER NOT NULL,
                    current_index INTEGER NOT NULL DEFAULT 0,
                    started_at INTEGER NOT NULL,
                    completed_at INTEGER
                );
                CREATE TABLE IF NOT EXISTS technical_session_questions (
                    session_id TEXT NOT NULL REFERENCES technical_interview_sessions(id) ON DELETE CASCADE,
                    question_id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    difficulty TEXT NOT NULL,
                    PRIMARY KEY (session_id, question_id)
                );
                CREATE TABLE IF NOT EXISTS technical_session_answers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL REFERENCES technical_interview_sessions(id) ON DELETE CASCADE,
                    question_id TEXT NOT NULL,
                    answer TEXT NOT NULL,
                    score INTEGER NOT NULL,
                    method TEXT NOT NULL,
                    correctness TEXT NOT NULL,
                    strengths TEXT NOT NULL,
                    missing_concepts TEXT NOT NULL,
                    suggestions TEXT NOT NULL,
                    ideal_answer TEXT NOT NULL,
                    answered_at INTEGER NOT NULL
                );
'''
assert needle in s
s=s.replace(needle,addition,1)
open(p,'w').write(s)
print('done')