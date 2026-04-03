# OJ_PROJECT (TryCode) — Interview Prep Notes (End-to-End)

This document explains **how this project works end-to-end**, what is **actually implemented in the current repo**, and how to discuss it in an interview for an SDE/Product Engineer role.

---

## 1) What this project is

**TryCode** is a Django-based “Online Judge” style web app where users can:

- Register / Login
- Browse Topics → Problems
- Open a problem page with a code editor
- Run code against a small subset of testcases (“Run”)
- Submit code against all testcases (“Submit”)
- View past submissions (mine / all)
- Get an AI review of their approach/solution using **Google Gemini**

**Core value**: a mini end-to-end OJ system including **problem storage**, **testcase evaluation**, **multi-language compilation/execution**, and **result persistence**.

---

## 2) Tech stack used in this repo

### Backend
- **Python + Django 5.2.4**
- Django Templates (server-rendered HTML)
- Django ORM for DB access

### Database
- **SQLite** configured in `oj_project/oj_project/settings.py` (current default)
- **PostgreSQL** present in `docker-compose.yml` as a service (but not wired into Django settings by default)

### Code execution (judge)
- `authentication/judge.py` uses `subprocess.run(...)` to execute user code.
- Supports:
  - Python
  - C++ (via `g++`)
  - Java (via `javac`, `java`)

### Frontend
- Django templates + CSS
- In-browser editor via **CodeMirror** (loaded from CDN)

### Containerization
- Dockerfile builds a Debian image and installs runtime tooling.
- `docker-compose.yml` defines the app + db.

---

## 3) Project structure (important folders/files)

- `oj_project/manage.py`
  - Django management entrypoint.

- `oj_project/oj_project/settings.py`
  - Django settings.
  - DB is SQLite currently.
  - `ALLOWED_HOSTS` includes `*` and localhost.
  - Gemini key is set via `GEMINI_API_KEY` constant (currently hardcoded).

- `oj_project/oj_project/urls.py`
  - Root URL routes:
    - `/admin/`
    - `/` → includes `authentication.urls`

- `oj_project/authentication/`
  - `models.py`: Topic, Problem, TestCase, Submission
  - `views.py`: all web flows
  - `judge.py`: code execution logic
  - `urls.py`: route definitions
  - `templates/`: HTML templates

- `docker-compose.yml`
  - Runs `web` + `db (postgres:14)`

- `oj_project/Dockerfile`
  - Builds image with python3, build tools, openjdk.

---

## 4) Data model (database schema)

Defined in `authentication/models.py`:

### Topic
- `name`
- `description`
- Relation: **Topic has many Problems** (`related_name='problems'`)

### Problem
- `topic` (FK → Topic)
- `title`
- `description`
- `input_format`
- `output_format`
- Relation: **Problem has many TestCases** (`related_name='testcases'`)

### TestCase
- `problem` (FK → Problem)
- `input_data`
- `expected_output`

### Submission
- `user` (FK → Django `User`)
- `problem` (FK → Problem)
- `code`
- `language` (python/cpp/java)
- `created_at`
- `verdict` (Accepted/Wrong Answer/Runtime Error/TLE/Compilation Error/Pending)
- `output`
- `error`

**What’s important to mention in interview**:
- Normalized relational design.
- Clear relationships: Topic→Problem→TestCase; Submission references User+Problem.
- Verdict/status stored for audit/history.

---

## 5) Main user flows + data flow (end-to-end)

### 5.1 Authentication flow
Routes (from `authentication/urls.py`):
- `/login/` → `login_view`
- `/register/` → `register_view`
- `/logout/` → `logout_view`

Data flow:
1. Browser sends POST with username/password.
2. Django uses `authenticate(...)` + `login(...)`.
3. Session cookie is set; subsequent requests are authenticated.

Security note:
- Uses Django’s built-in password hashing and session auth.
- Login/register are standard server-rendered forms.

### 5.2 Browse topics → problems
Routes:
- `/topics/` → `topic_list_view`
- `/topics/<topic_id>/problems/` → `problem_list_view`

Data flow:
1. `topic_list_view` queries all topics.
2. It calculates progress by counting distinct accepted submissions per topic.
3. Render `topic.html`.

Important implementation detail:
- `problem_list_view` currently slices problems: `topic.problems.all()[:5]`.
  - So UI shows **up to 5 problems per topic** even though DB can store unlimited.

### 5.3 Problem page + run/submit evaluation
Route:
- `/problems/<problem_id>/` → `problem_detail_view`

GET data flow:
1. Fetch `Problem` and its `TestCase`s.
2. Render `problem_page.html`.
3. CodeMirror initializes editor, supports language switching.

POST data flow (Run vs Submit):
1. User submits form with `code`, `language`, and `action`.
2. Server loads testcases for the problem.
3. If `action == run` → evaluates only first 2 testcases.
4. If `action == submit` → evaluates **all** testcases.
5. For each testcase:
   - call `evaluate_code(code, language, test.input_data)`
   - compare `stdout.strip()` with `expected_output.strip()`
6. Compute final verdict.
7. If `submit`:
   - create `Submission` row with verdict, output, error.
8. Render response HTML with verdict + testcase results.

**Key interview talking points**:
- Separation between web layer (`views.py`) and evaluation engine (`judge.py`).
- Deterministic judging: output compared to expected output.
- Persisting submission history in DB.

### 5.4 Submission history
Routes:
- `/submissions/` → `all_submissions_view`
- `/my-submissions/` → `my_submissions_view`
- `/submission/<submission_id>/` → `submission_detail_view`

Data flow:
- Uses `.select_related(...)` for joining `problem`/`user` efficiently in list pages.
- Orders by latest first.

### 5.5 AI Review flow (Gemini)
Route:
- `/ai-review/` → `ai_review_view`

Data flow:
1. User submits problem_id + optionally code.
2. Server forms a prompt including problem description and code.
3. Calls Gemini via `google.generativeai`.
4. Renders `problem_page.html` with `ai_response`.

Important note:
- `ai_review_view` has `@csrf_exempt` currently.
- It also uses `@login_required`.

---

## 6) Code execution engine details (`authentication/judge.py`)

### 6.1 How execution works
`evaluate_code(code, language, input_data)`:

1. Creates/uses `./temp` directory.
2. Writes user code to a temporary file using a UUID-based filename.
3. Depending on language:
   - **Python**: runs `python3 file.py`
   - **C++**:
     - compiles: `g++ file.cpp -o file_exe`
     - runs the executable
   - **Java**:
     - writes to `Main.java`
     - compiles: `javac Main.java`
     - runs: `java -cp temp Main`
4. Executes with:
   - `input=input_data.encode()`
   - `stdout=PIPE`, `stderr=PIPE`
   - `timeout=2` seconds
5. Returns `(stdout, stderr)`.
6. Finally block cleans up temp files.

### 6.2 Constraints implemented
- **Time limit**: 2 seconds per testcase (hard-coded via `timeout=2`).
- **Compilation error handling**:
  - C++: `subprocess.CalledProcessError` returns “Compilation Error”.
  - Java: checks compile return code and returns stderr.

### 6.3 What is NOT implemented (important to be honest)
- No sandboxing / container-per-submission.
- No OS-level resource limits (memory, CPU, file access).
- No concurrency control/queue (it runs in the request thread).
- Potential risk: user code can attempt malicious operations.

---

## 7) Docker & isolation (what is implemented here)

### 7.1 Dockerfile
`oj_project/Dockerfile`:
- Base: `debian:bullseye`
- Installs:
  - `python3`, `python3-pip`
  - `build-essential` (for C++ compilation)
  - `openjdk-17-jdk` (for Java compilation)
- Copies project into container
- Installs Python dependencies from `requirements.txt`
- Exposes port `8000`
- Runs: `python3 manage.py runserver 0.0.0.0:8000`

### 7.2 docker-compose.yml
- `web` service:
  - builds from repo
  - maps port `8000:8000`
  - mounts repo directory into container (`volumes: - .:/app`)
  - depends on `db`
  - loads `.env`

- `db` service:
  - `postgres:14`
  - sets DB name/user/password

### 7.3 What “isolation” you get
Docker gives:
- Process isolation (namespaces) and filesystem separation.
- Reproducible environment for dependencies.

But **in this repo’s current design**:
- The judge executes user code inside the same container/process context as the Django server.
- So this is not strong sandbox isolation (it’s “containerized app”, not “sandboxed untrusted code”).

**Interview-safe explanation**:
- “Docker is used to standardize environment and ensure compilers/interpreters exist. For production-grade OJ, I would execute submissions in a dedicated sandbox/container per run, with strict resource limits.”

---

## 8) Security mechanisms (what’s present vs missing)

### Implemented
- Django session authentication
- CSRF middleware enabled globally
- UUID temp filenames
- Cleanup of temp artifacts

### Gaps to mention (and how you’d improve)
- Secrets are hardcoded in settings (should be env vars)
- `DEBUG=True` in `settings.py` (production should be False)
- `ALLOWED_HOSTS=['*', ...]` is insecure for production
- `@csrf_exempt` on AI review endpoint (should be removed unless there’s a reason)
- Judge runs untrusted code without sandbox/resource isolation

---

## 9) Concurrency & scaling (system design discussion)

### What the current project supports
- Django dev server is single-process by default.
- Each request that does judging blocks the request until completion.
- Concurrent submissions are limited by:
  - server worker count
  - CPU
  - the fact that evaluation loops through testcases sequentially

### How you’d scale it (talking points)
1. **Switch to a production server**:
   - Gunicorn/Uvicorn workers behind Nginx.
2. **Async task queue**:
   - Celery + Redis/RabbitMQ so judge runs in background.
3. **Separate services**:
   - Web/API service
   - Judge workers
   - DB service
   - Cache service
4. **Caching**:
   - Cache problem/testcase lists.
5. **DB indexing**:
   - indexes on `Submission(user, created_at)`, `Submission(problem, verdict)` etc.
6. **Load balancer**:
   - Nginx/ALB distributing requests across multiple web instances.

---

## 10) Common interview questions & good answers

### Q1: “Walk me through what happens when a user clicks Submit.”
Answer structure:
- URL → view → fetch problem/testcases → call judge per testcase → compare outputs → verdict → store Submission → render result.

### Q2: “How do you enforce time limit?”
- `subprocess.run(..., timeout=2)`.
- Mention improvement: per-language, per-problem configurable limits and CPU quotas.

### Q3: “How do you prevent malicious code execution?”
- Current: not fully prevented.
- Proposed: sandbox (Docker-per-run, seccomp, AppArmor), filesystem restrictions, network disabled, resource limits.

### Q4: “How would you handle 1,000 concurrent submissions?”
- Queue + async workers (Celery), autoscaling workers, store results async, show “Pending” status.

### Q5: “How would you reduce DB load?”
- Use caching for reads, indexes, and optimize queries with `select_related/prefetch_related`.

---

## 11) Quick checklist for your interview demo

- Can you run app locally?
- Can you create a Topic/Problem/Testcases from Django admin?
- Can you show run vs submit behavior?
- Can you show stored submissions list?
- Can you trigger AI review?

---

## 12) Suggested improvements (optional to mention)

- Move secrets to environment variables (`SECRET_KEY`, Gemini API key)
- Remove `@csrf_exempt` from AI review
- Add rate limiting for submit endpoints
- Add DB indexes in `models.py` via `Meta.indexes`
- Introduce Celery for background judging
- Add per-problem time limits and memory constraints

---

# Appendix A — Current endpoints

From `authentication/urls.py`:
- `/` home
- `/login/`, `/register/`, `/logout/`
- `/welcome/`
- `/topics/`
- `/topics/<topic_id>/problems/`
- `/problems/<problem_id>/`
- `/submissions/`, `/my-submissions/`
- `/submission/<submission_id>/`
- `/ai-review/`
