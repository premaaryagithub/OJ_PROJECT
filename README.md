# TryCode — Online Judge Platform

A full-stack **Online Judge** built with Django, featuring multi-language code execution, AI-powered code review via Google Gemini, and a topic-based problem management system.

---

## Features

- **Multi-language Code Execution** — Supports Python, C++, and Java with isolated subprocess-based execution
- **Run & Submit Modes** — "Run" tests against the first 2 sample cases; "Submit" evaluates all test cases and persists the verdict
- **AI Code Review** — Integrates Gemini 2.5 Flash to review user submissions or suggest approaches for unsolved problems
- **Topic-based Problem Browser** — Problems are grouped by topics with per-user progress tracking (% solved per topic)
- **Authentication** — Django session-based auth with register, login, and logout
- **Submission History** — Per-user and global submission views with detailed verdict breakdown
- **Dockerized** — Multi-service Docker setup with Python 3, OpenJDK 17, and g++ pre-installed for code execution

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 4.2 |
| Database | SQLite (dev) / PostgreSQL (Docker/prod) |
| Code Execution | `subprocess` + `uuid`-isolated temp files |
| AI Integration | Google Gemini 2.5 Flash (`google-generativeai`) |
| Containerization | Docker + Docker Compose |
| Deployment | Render (`render_build.sh`) |

---

## Project Structure

```
OJ_PROJECT/
├── oj_project/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── db.sqlite3
│   ├── temp/                        # Temp files for code execution (auto-cleaned)
│   ├── oj_project/
│   │   ├── settings.py
│   │   └── urls.py
│   └── authentication/              # Core Django app
│       ├── models.py                # Topic, Problem, TestCase, Submission
│       ├── views.py                 # All request handlers
│       ├── judge.py                 # Code execution engine
│       ├── urls.py                  # URL routing
│       ├── forms.py
│       ├── admin.py
│       ├── migrations/
│       └── templates/               # HTML templates
│           ├── base.html
│           ├── home.html
│           ├── topic.html
│           ├── problem_list.html
│           ├── problem_page.html
│           ├── submissions.html
│           ├── my_submission.html
│           └── submission_detail.html
├── docker-compose.yml
├── render_build.sh
└── requirements.txt
```

---

## Data Models

### `Topic`
Groups related problems together.

```python
name: CharField
description: TextField
```

### `Problem`
A coding problem linked to a topic.

```python
topic: FK(Topic)
title: CharField
description: TextField
input_format: TextField
output_format: TextField
```

### `TestCase`
Input/output pairs tied to a problem, used for evaluation.

```python
problem: FK(Problem)
input_data: TextField
expected_output: TextField
```

### `Submission`
Records each user submission with full verdict metadata.

```python
user: FK(User)
problem: FK(Problem)
code: TextField
language: CharField         # python | cpp | java
verdict: CharField          # Accepted | Wrong Answer | Runtime Error | TLE | CE | Pending
output: TextField
error: TextField
created_at: DateTimeField

# DB indexes for fast lookup
Index(user, -created_at)
Index(problem, verdict)
```

---

## Code Execution Engine (`judge.py`)

The judge creates a **UUID-named temp file** per submission, compiles/runs it in a subprocess, and enforces a **2-second timeout**.

```python
def evaluate_code(code, language, input_data) -> (stdout, stderr):
```

**Flow by language:**

- **Python** → writes `.py` file, runs `python3 <file>`
- **C++** → writes `.cpp`, compiles with `g++ <file> -o <exe>`, runs the binary
- **Java** → writes `Main.java`, compiles with `javac`, runs with `java -cp <folder> Main`

**Cleanup**: temp source files, executables, and `.class` files are always deleted in a `finally` block regardless of outcome.

**Handled error cases:**
- `subprocess.CalledProcessError` → Compilation Error
- `subprocess.TimeoutExpired` → Time Limit Exceeded
- Any other `Exception` → Runtime Error with message

---

## URL Routes

| Method | URL | View | Auth Required |
|---|---|---|---|
| GET | `/` | `home_view` | No |
| GET | `/welcome/` | `welcome_page_view` | Yes |
| GET/POST | `/login/` | `login_view` | No |
| GET/POST | `/register/` | `register_view` | No |
| GET | `/logout/` | `logout_view` | No |
| GET | `/topics/` | `topic_list_view` | Yes |
| GET | `/topics/<id>/problems/` | `problem_list_view` | Yes |
| GET/POST | `/problems/<id>/` | `problem_detail_view` | Yes |
| GET | `/submissions/` | `all_submissions_view` | Yes |
| GET | `/my-submissions/` | `my_submissions_view` | Yes |
| GET | `/submission/<id>/` | `submission_detail_view` | Yes |
| POST | `/ai-review/` | `ai_review_view` | Yes |

---

## AI Review (`/ai-review/`)

Powered by **Gemini 2.5 Flash**. Accepts a POST with `problem_id`, `code`, and `language`.

- If code is provided → Gemini reviews the solution against the problem description
- If no code is provided → Gemini suggests an approach to solve the problem

```python
model = genai.GenerativeModel('gemini-2.5-flash')
response = model.generate_content(f"Give me a brief review on this:\n{prompt}")
```

---

## Setup & Run

### Local (without Docker)

```bash
# 1. Clone the repo
git clone https://github.com/premaaryagithub/OJ_PROJECT.git
cd OJ_PROJECT/oj_project

# 2. Create and activate virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Set environment variables (create a .env file)
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key

# 5. Run migrations
python manage.py makemigrations
python manage.py migrate

# 6. Create superuser (to add topics/problems via admin)
python manage.py createsuperuser

# 7. Start the server
python manage.py runserver
```

Visit `http://127.0.0.1:8000` — admin panel at `/admin/`.

### With Docker

```bash
# From repo root
docker-compose up --build
```

The `docker-compose.yml` spins up two services:
- `web` — Django app on port `8000`
- `db` — PostgreSQL 14 (`oj_db` / `admin` / `secret`)

> **Note:** Switch `DATABASES` in `settings.py` from SQLite to PostgreSQL when using Docker.

---

## Environment Variables

| Variable | Description |
|---|---|
| `SECRET_KEY` | Django secret key |
| `GEMINI_API_KEY` | Google Gemini API key |
| `DJANGO_SETTINGS_MODULE` | Set to `oj_project.settings` |

---

## Deployment (Render)

The `render_build.sh` script handles Render deployments:

```bash
pip install -r requirements.txt
cd oj_project
python manage.py makemigrations
python manage.py migrate
```

The app is live at: `https://oj-project-3puf.onrender.com`

---

## Adding Problems

Use Django Admin at `/admin/`:

1. Create a **Topic** (e.g., "Arrays", "Binary Search")
2. Create a **Problem** under that topic with description, input format, output format
3. Add **TestCases** for the problem — each with `input_data` and `expected_output`

---

## Supported Languages

| Language | Compiler/Runtime | Timeout |
|---|---|---|
| Python | `python3` | 2 seconds |
| C++ | `g++` | 2 seconds |
| Java | `javac` + `java` (OpenJDK 17) | 2 seconds |

> Java submissions must use `Main` as the class name.

---

## Known Limitations

- Code execution runs directly on the host (no sandboxing/cgroups isolation) — avoid running untrusted code in production without additional hardening
- SQLite is used by default; switch to PostgreSQL for production
- Java file is always written as `Main.java`, so concurrent Java submissions may conflict — UUID-based file naming for Java is a future improvement

---


