# TryCode — Online Judge

A full-stack online judge built during my Software Engineering Externship at **AlgoUniversity (YC S21)**. Supports multi-language code execution, AI-powered code review, and topic-based problem management.

**Live:** https://oj-project-3puf.onrender.com

---

## Tech Stack

`Django 5.2` · `PostgreSQL` · `SQLite (dev)` · `Docker` · `Google Gemini 2.5 Flash` · `OpenJDK 17` · `g++`

---

## Key Features

- **Multi-language execution** — Python, C++, Java via subprocess with 2s timeout and UUID-isolated temp files
- **Run vs Submit** — Run tests first 2 cases for quick feedback; Submit evaluates all cases and persists verdict
- **AI Code Review** — Gemini reviews your solution or suggests an approach if no code is provided
- **Topic progress tracking** — Problems grouped by topic with per-user % solved
- **Session auth** — Register, login, logout with `@login_required` on all protected routes

---

## Architecture

```
authentication/
├── models.py      # Topic → Problem → TestCase → Submission (with DB indexes)
├── judge.py       # Code execution engine (compile → run → verdict)
├── views.py       # All request handlers
└── urls.py        # 12 routes

oj_project/
├── settings.py
└── urls.py

Dockerfile          # debian:bullseye + python3 + g++ + openjdk-17
docker-compose.yml  # web (Django) + db (Postgres 14)
```

---

## Quick Start

```bash
git clone https://github.com/premaaryagithub/OJ_PROJECT.git
cd OJ_PROJECT/oj_project

python -m venv venv && source venv/bin/activate
pip install -r requirements.txt

# .env
SECRET_KEY=your-secret-key
GEMINI_API_KEY=your-gemini-api-key

python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

**With Docker:**
```bash
docker-compose up --build
```

Add problems via Django Admin at `/admin/` → Topic → Problem → TestCases.

---

## Known Limitations

- No sandbox/cgroups isolation — subprocess runs directly on host
- Java submissions must use `Main` as class name (concurrent conflict known)
