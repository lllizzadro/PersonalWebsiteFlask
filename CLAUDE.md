# Personal Website — Flask (Python)

A toy/personal website built by **Louis Lizzadro** to learn web development, Python/Flask, and Claude Code. Built **in parallel** with a Go/Gin twin repo, [PersonalWebsiteGin](https://github.com/lllizzadro/PersonalWebsiteGin) — every feature is built here in Flask **first**, then mirrored in Gin.

## About Louis
- Software developer learning web dev. GitHub: `lllizzadro`.
- **Hands-on learner — this matters.** Guide him to write the code himself: explain the concept and what's needed, let him implement it, then review what he wrote and explain any mistakes. Only write code directly when demonstrating a brand-new concept for the first time, or when he's stuck after trying.

## Stack & conventions
- **Flask + Jinja** templates in `templates/`. `base.html` is the layout; pages use `{% extends "base.html" %}` + `{% block content %}`.
- **Tailwind CSS via CDN** (`<script src="https://cdn.tailwindcss.com">`) — no build step.
- **SQLite** via stdlib `sqlite3`. Open a fresh connection per request with `get_db()` (which sets `row_factory = sqlite3.Row` for named columns). `init_db()` runs once at module level (not in `__main__`, so it also works under gunicorn).
- **Always use parameterized queries** (`?` placeholders) — never string-format user input (SQL injection).
- State-changing forms use the **POST/Redirect/GET** pattern.
- Client-side JS lives in `static/js/`; load it with `{{ url_for('static', filename='js/...') }}`.

## Run
```
pip install -r requirements.txt
python app.py        # http://localhost:5000
```
Production target: **gunicorn** (already in requirements.txt); external hosting is planned, so keep secrets in env vars.

## Progress
- ✅ Home (`/`) — bio + projects list
- ✅ Guestbook (`/guestbook`) — SQLite-backed, form + POST/Redirect/GET
- ✅ Dice roller (`/dice`) — client-side JS in `static/js/dice.js`
- ⏭️ **Next: styling pass** — convert the guestbook `<table>` to mobile-friendly cards, learn Tailwind responsive breakpoints (`sm:`/`md:`/`lg:`), and style the form inputs.
