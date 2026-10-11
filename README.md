# GenAssess

GenAssess includes a FastAPI backend and a Next.js, React, TypeScript, and Tailwind CSS frontend. Users choose whether they are looking for a job or hiring before signing in. Recruiters can submit company details for registry checks and admin review before publishing jobs.

## Authentication features

- Account registration with validated name, email, and password.
- Candidate/job seeker and recruiter/hiring account selection.
- Optional Google sign-in through Supabase Auth.
- Optional mobile number collected as a contact detail (no paid SMS verification).
- Argon2 password hashing; only the password hash is stored.
- JWT session cookie marked HttpOnly, SameSite=Lax, and Secure when configured.
- SQLite-backed users and revocable login sessions.
- Protected `GET /auth/me`, plus register, login, and logout endpoints.
- Login/Register pages and a session-checked dashboard.
- Manual CIN/MCA or GSTIN verification, followed by website and LinkedIn review.
- Recruiter job publishing endpoints blocked until the company is approved.
- Admin review queue restricted to `VERIFICATION_ADMIN_EMAILS`.

## Requirements

- Python 3.10+
- Node.js 20.9+
- npm

## Backend setup and run (PowerShell)

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
if (!(Test-Path .env)) { Copy-Item .env.example .env }
python -c "import secrets; print(secrets.token_urlsafe(48))"
# Put the generated value on the JWT_SECRET= line in .env; keep this file private.
# For local HTTP development, set COOKIE_SECURE=false in .env.
.\.venv\Scripts\python.exe -m uvicorn app:app --reload
```

Keep this terminal open. The backend loads `.env`, validates the JWT secret, and creates the SQLite database and tables at startup. `JWT_SECRET` must be a random value of at least 32 bytes. Keep it stable between restarts so existing sessions remain valid. The example sets `COOKIE_SECURE=false` only for local HTTP; use `true` when serving over HTTPS.

To enable Google sign-in, create a Supabase project and set `SUPABASE_URL` and `SUPABASE_ANON_KEY` in `.env`. Configure the Google provider in Supabase Auth and allow `http://localhost:3000/auth/callback` as a redirect URL. Use the same project URL and publishable/anon key in `frontend/.env.local` as `NEXT_PUBLIC_SUPABASE_URL` and `NEXT_PUBLIC_SUPABASE_ANON_KEY`. Supabase provider buttons remain unavailable until those frontend values are set. The backend validates the Supabase access token with the Supabase Auth user endpoint, then issues GenAssess's HttpOnly session cookie. Email/password sign-in works without an external provider. Phone numbers are optional contact details; SMS OTP is intentionally not used to avoid SMS charges. Hosted free-tier limits apply and may change.

Company verification uses no third-party registry API. Recruiters submit a CIN or GSTIN, website, and LinkedIn URL; a reviewer checks the identifier in the official MCA/GST portals and manually reviews the social links. Set `VERIFICATION_ADMIN_EMAILS` to a comma-separated list of reviewer account emails. Reviewers sign in to GenAssess and open `/admin/verifications`. This trades API fees for manual review time.

## Frontend setup and run

Open a second PowerShell terminal at the project root:

```powershell
if (!(Test-Path frontend\.env.local)) { Copy-Item frontend\.env.example frontend\.env.local }
Set-Location frontend
npm install
npm run dev
```

Open `http://localhost:3000`. The frontend sends credentialed requests to `http://localhost:8000` by default. To use a different backend URL, set `NEXT_PUBLIC_API_URL` in `frontend/.env.local` and restart Next.js.

## Test authentication

Run the tests from the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

The tests cover registration and duplicate emails, optional phone contact validation, request validation, hashed password storage, cookie-based login, protected `/auth/me`, logout revocation, rejected cross-origin writes, role migration, manual company review, and server-side job-posting enforcement.

The API returns user details but not password hashes or bearer tokens. The JWT is held in the HttpOnly cookie, so frontend JavaScript cannot read or store it. Logout revokes the corresponding session in SQLite and clears the cookie.

## Candidate and recruiter roles

At the start, choose “I'm looking for a job” or “I'm hiring”; the selected role is stored when the account is created and is not overwritten on later sign-ins. Recruiter accounts can use the dashboard, but cannot publish jobs until a reviewer manually checks the company identifier and approves its profile. To promote an existing local account during development, use this backend-operator command:

```powershell
.\.venv\Scripts\python.exe -m scripts.set_user_role recruiter@example.com RECRUITER
```

The script updates the server-side SQLite record and is not exposed as an API route. Login and `/auth/me` return the stored role, while each dashboard and recruiter API endpoint independently checks the current database role against the HttpOnly session.

Job seeker login opens `/candidate/dashboard`; candidate practice starts at `/candidate/practice`. The candidate flow links to `/candidate/practice/aptitude` for instructions, `/candidate/practice/aptitude/test?sessionId=...` for an assessment, `/candidate/practice/aptitude/result?sessionId=...` for results, and `/candidate/practice/history` for session history. Role-protected pages redirect unauthenticated users to sign-in and users with the other role to their own dashboard.

Hiring team login opens `/recruiter/dashboard`; company verification is at `/recruiter/company-verification`, and job posting is at `/recruiter/jobs/new`. `/recruiter/applicants` and `/recruiter/evaluation` are role-protected Coming Soon pages; application tracking and recruiter interview evaluation do not have backend implementations yet. The API enforces company approval even if a recruiter bypasses the frontend.

To test both roles locally, create a job seeker account and a separate hiring account from the role-selection page. For admin review, add the reviewer's email to `VERIFICATION_ADMIN_EMAILS`, sign in with that email, and open `/admin/verifications`.

## Candidate aptitude practice (Round 1)

The candidate practice flow currently implements only Aptitude & Reasoning:

1. Open `/candidate/practice` and choose target role, company type, and experience level.
2. Review the assessment structure at `/candidate/practice/aptitude`.
3. Start or resume a timed attempt at `/candidate/practice/aptitude/test?sessionId=...`.
4. Submit the test or let the server-enforced deadline expire; review deterministic scoring and topic/difficulty analysis at `/candidate/practice/aptitude/result?sessionId=...`.

The backend keeps three layers separate: `src/aptitude/bank.py` defines question content and metadata; `src/aptitude/selection.py` selects a category-balanced, difficulty-balanced set; `src/aptitude/routes.py` creates and evaluates persisted sessions. The SQLite tables `aptitude_questions`, `aptitude_practice_sessions`, `aptitude_session_questions`, and `aptitude_practice_answers` retain the bank, delivered question set, answer/review state, timestamps, and results. Correct answers are not returned while a session is in progress. Startup seeds the bank idempotently and only updates an existing question definition if no session has used it, preserving historic results.

The current aptitude bank retains 71 original GenAssess-authored questions. IndiaBix and similar placement-test resources informed topic organization and common patterns only; their questions were not scraped or copied. The supplied Hugging Face `Prathamesh25/aptitude-qa-dataset` was inspected directly: all 1,769 rows use chat-style question/solution messages and do not provide the four answer choices required by the live aptitude session schema. We did not invent distractors or import those records into the aptitude selector. The Hugging Face dataset card and README declare Apache-2.0.

By default, each session has 20 questions (8 quantitative, 6 logical, 6 verbal) with an Easy/Medium/Hard distribution of 30/50/20. To configure the structure, set these optional JSON environment variables in the backend `.env`:

```dotenv
APTITUDE_CATEGORY_COUNTS='{"Quantitative Aptitude":8,"Logical Reasoning":6,"Verbal Ability":6}'
APTITUDE_DIFFICULTY_DISTRIBUTION='{"Easy":30,"Medium":50,"Hard":20}'
```

Counts must use supported categories and total no more than 80; the difficulty percentages must total 100. Topic performance increases future selection weight for weaker topics. Overall past accuracy and experience level shift the difficulty distribution in bounded increments. Previously unseen questions are preferred before previously delivered questions; questions are authored for GenAssess and are not scraped from third-party question sites. Session timestamps and answer persistence are server-side, and expired attempts are automatically finalized when accessed or submitted.

Run aptitude and existing backend tests from the project root:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Run frontend quality checks from `frontend`:

```powershell
npm run lint
npx tsc --noEmit
npm run build
```

## Four-round question-bank foundations

The aptitude test remains the only round connected to the candidate assessment flow. Separate typed data banks are now ready for the other rounds under `src/question_banks/`; their shared metadata includes question ID, prompt, category, topic, difficulty, source, and license. Optional fields support explanations, coding reference solutions and test cases, and behavioral follow-up/evaluation dimensions.

| Round | Current bank | Source and handling |
| --- | ---: | --- |
| Aptitude & Reasoning | 71 | Original GenAssess questions. The 1,769-row Apache-2.0 dataset was screened but not imported because its records do not satisfy the current multiple-choice schema. |
| Technical Concepts | 20 | Original GenAssess question/answer records across Python, Java, C/C++, OOP, DBMS, SQL, operating systems, networks, DSA, and software engineering. |
| Coding Challenge | 5 | Selected from the sanitized MBPP train split; each retains its task ID, reference solution, three test cases, source, attribution, and CC-BY-4.0 metadata. |
| Behavioral / HR | 50 | Original GenAssess prompts, five in each of the ten requested categories, with structured follow-up dimensions and deterministic evaluation criteria. |

`src/question_banks/source_audit.py` records the source revisions, licenses, inspected/imported/filtered counts, and selection decisions. Stack Overflow is not copied into the technical bank: a public post sample contains HTML, tags, and a post-specific content license, while the official licensing page documents date-dependent CC BY-SA terms. The data.stackexchange.com interface returned HTTP 403 during inspection, so a public Stack Exchange API question sample and official licensing guidance were used instead. HumanEval's MIT license and prompt/solution/test schema were inspected, but its 164-task set was not imported; MBPP is the initial source and no isolated execution sandbox exists.

MBPP solutions and test cases are stored as inert question-bank data only. GenAssess does not compile or execute candidate submissions; safe code execution requires a separately designed sandbox and is not part of this data-layer work.

To run focused bank and aptitude validation:

```powershell
.\.venv\Scripts\python.exe -m pytest tests\test_question_banks.py tests\test_aptitude.py -q
```

## Existing interview logic

`app.py` now starts the FastAPI backend; it no longer launches a Gradio interface. The interview domain code remains in `src/interview.py`, `src/evaluator.py`, `src/question_generator.py`, and `src/question_bank.py`, with its existing tests. It is not connected to the authenticated dashboard or API yet.
