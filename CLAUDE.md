# Personal Website — Flask (Python)

A personal website built and maintained by **Louis Lizzadro**. It was originally built in parallel with a Go/Gin twin to learn web dev, but as of 2026-06-14 **this Flask version is the single canonical site** — the Gin version has been retired (archived for reference, no longer maintained). Work only happens here now.

## About Louis
- Software developer learning web dev. GitHub: `lllizzadro`.
- **Hands-on learner — this matters.** Guide him to write the code himself: explain the concept and what's needed, let him implement it, then review what he wrote and explain any mistakes. Only write code directly when demonstrating a brand-new concept for the first time, or when he's stuck after trying. (He also validates the UI himself — don't generate screenshots unless asked.)

## Stack & conventions
- **Flask + Jinja** templates in `templates/`. `base.html` is the layout; pages use `{% extends "base.html" %}` + `{% block content %}`.
- **Tailwind CSS via CDN** (`<script src="https://cdn.tailwindcss.com">`) — no build step. Config is set inline in `base.html`'s `<head>` via `tailwind.config`.
- **SQLite** via stdlib `sqlite3`. Connection is opened lazily per request in `get_db()`, stashed on Flask's `g`, and closed automatically by a `@app.teardown_appcontext` (`close_db`) — no per-route `db.close()`. `get_db()` sets `row_factory = sqlite3.Row` for named columns. The DB path comes from `DB_PATH = os.environ.get('DATABASE_PATH', 'guestbook.db')` (local default; prod points it at the Fly volume — see Deployment). `init_db()` runs once at module level using its **own** plain `sqlite3.connect(DB_PATH)` (NOT `get_db()` — `g` only exists during a request; module-level code has no app context). Module-level init means it also works under gunicorn.
- **Always use parameterized queries** (`?` placeholders) — never string-format user input (SQL injection).
- **Secrets via env vars.** `app.secret_key = os.environ.get('SECRET_KEY', 'dev')` — used to sign the session cookie (currently powers `flash()` messages; also needed for any future login/CSRF). The `'dev'` fallback is local-only; prod sets a real random key (`python3 -c "import secrets; print(secrets.token_hex(32))"`) via Fly secrets.
- State-changing forms use the **POST/Redirect/GET** pattern. Server-side input validation in `add_message()`: `.strip()` at read time, reject empty, enforce length (name ≤ 50, message ≤ 1000) — server checks mirror the form's `maxlength`. Failures use `flash()` + redirect; `base.html` renders flashes via `get_flashed_messages()` above `{% block content %}`. (NOTE: flash banner uses undefined CSS classes `flash-messages`/`flash-message` — still needs Tailwind styling.)
- Client-side JS lives in `static/js/`; load it with `{{ url_for('static', filename='js/...') }}`. Current scripts: `theme.js` (dark-mode toggle), `localtime.js` (per-visitor local timestamps).

## Theming
- **Accent:** `purple-600`. **Gray base:** `neutral` (chosen over `slate`, which looked too blue under purple).
- **Fonts:** Inter (body) + Space Mono (headings/brand), loaded via Google Fonts `<link>`. Set in `tailwind.config` `fontFamily` (`sans`=Inter, `mono`=Space Mono); headings get Space Mono via a base `<style> h1,h2,h3` rule; the nav brand uses the `font-mono` class.
- **Dark mode:** Tailwind `darkMode: 'class'`. A sun/moon toggle button (`#theme-toggle`) flips the `dark` class on `<html>`; `theme.js` does `classList.toggle` + saves to `localStorage`. An **inline `<head>` init script** applies the saved/system theme before paint (prevents flash + persists across loads). Icons swap via `dark:hidden` / `hidden dark:inline`. Cards use `dark:hover:bg-neutral-700` because shadow-based hover is invisible on dark backgrounds.
- **Timestamps:** stored UTC; shown in each visitor's local time. The `<time>` element carries an ISO-UTC `datetime` attr (Jinja `| isodate` filter) with a `| prettydate` fallback; `localtime.js` rewrites it with `toLocaleString`.

## Run
```
pip install -r requirements.txt
python app.py        # http://localhost:5000
```
To view on another device on the LAN: `python -m flask --app app run --host=0.0.0.0 --port=5000`, then visit `http://<computer-LAN-IP>:5000`.
Production target: **gunicorn** (in requirements.txt); external hosting is planned, so keep secrets in env vars.

## Deployment — Fly.io (in progress as of 2026-06-16)
Chosen over PythonAnywhere/Render to learn real deployment skills + because Fly supports a **persistent volume** for SQLite (Render's free tier wipes the disk on each deploy). Account: `lllizzadro`. App name: `lllizzadro` → `https://lllizzadro.fly.dev`. Region: `ord`.

**Files added this session** (all in repo root): `Dockerfile` (python:3.13-slim, installs requirements before `COPY . .` for layer caching, `EXPOSE 8080`, `CMD gunicorn --bind 0.0.0.0:8080 app:app`), `.dockerignore` (`.venv/`, `__pycache__/`, `*.db`, `.git/`, `.env`), and `fly.toml` (`internal_port = 8080`; `[env] DATABASE_PATH = "/data/guestbook.db"`; `[mounts] source = "data"`, `destination = "/data"`).

**Infra already provisioned:** volume `data` (1 GB, `ord`, encrypted, scheduled snapshots on) created with `fly volumes create data --region ord --size 1`; `SECRET_KEY` set via `fly secrets set` (shows **Staged** — applies on first deploy, no separate `fly secrets deploy` needed). Why it all ties together: `DATABASE_PATH` → `/data/guestbook.db` lands the DB on the mounted volume so guestbook data survives redeploys. Keep this app at **one machine** — a volume binds to a single machine; scaling out would diverge the SQLite data.

**✅ DEPLOYED (2026-06-16):** live at https://lllizzadro.fly.dev — first `fly deploy` succeeded and the URL was confirmed up. Volume-persistence check (sign guestbook → redeploy → entry still there) being verified. Useful ops: `fly status`, `fly open`, `fly logs`, `fly ssh console` (root shell; only `/data` persists), `fly ssh sftp` (pull/push the DB file).

**CI/CD — push-to-deploy (set up 2026-06-16):** `fly launch` auto-generated `.github/workflows/fly-deploy.yml`, which runs `flyctl deploy --remote-only` **on push to `main`** (only `main` — pushing `dev` or opening a PR does NOT deploy; the deploy fires when a PR is **merged** to `main`, i.e. `main` = production). So the workflow is: do work on `dev` → PR → merge to `main` to go live. To finish enabling it:
- The workflow needs a `FLY_API_TOKEN` GitHub Actions secret: `fly tokens create deploy`, then add it under GitHub repo → Settings → Secrets and variables → Actions (name exactly `FLY_API_TOKEN`).
- Pushing the workflow file requires a PAT with the **`workflow`** scope (or use an SSH remote) — GitHub rejects workflow-file changes from a token lacking it.

**Cross-machine note:** with the CI above, any machine that can `git push` to `main` (incl. Windows, browser-only) ships automatically — no local `flyctl`/Docker needed. For manual deploys from Windows instead, install flyctl: `iwr https://fly.io/install.ps1 -useb | iex`. The Fly **web dashboard** (fly.io/dashboard) monitors/manages from any OS but cannot deploy code itself.

## Status
- ✅ Home (`/`) — bio + projects list
- ✅ Guestbook (`/guestbook`) — SQLite-backed, form + POST/Redirect/GET, card layout, local-time timestamps. Hardened this session: `g`/teardown DB cleanup, env-var `SECRET_KEY`, server-side validation + flash feedback.
- ✅ Styling pass complete — purple/neutral theme, dark mode w/ toggle, Inter/Space Mono fonts, responsive foundation
- ✅ Deployment to Fly.io — **live** at https://lllizzadro.fly.dev (see Deployment section).
- ⏭️ Possible next (mostly deferred until after deploy):
  - **New pages** — `/now` and `/uses` are the best effort/reward; also `/resume` (CV page — could embed/link a PDF or render structured experience), bookmarks, blog. When nav outgrows the space, add a responsive hamburger menu.
  - **Wall of curated links (chosen guestbook glow-up)** — Louis likes this direction. Evolve the guestbook into a public, crowd-sourced **feed of cool links** visitors submit: instead of "name + message," each submission is a link (URL + title + optional short description/blurb), rendered as a growing curated wall. Reuses the existing form + SQLite + POST/Redirect/GET + validation infra rather than starting fresh. Build notes: new/extended table (url, title, description, submitter name, timestamp); validate the URL server-side (scheme allow-list http/https — don't render `javascript:` etc.); links open in a new tab with `rel="noopener noreferrer"`; pairs naturally with the deferred **CSRF protection** since it's a public write endpoint (spam/abuse risk). Could replace or live alongside the current guestbook.
  - **Form/security hardening** — add **CSRF protection** (Flask-WTF + `{{ csrf_token() }}`); guestbook form currently unprotected. Style the flash banner. Empty-state for guestbook ("be the first").
  - **DB evolution** — stay on SQLite for now (right call at this scale). Revisit **SQLAlchemy + Postgres** when building a relation-heavy feature (e.g. blog) or if horizontal scaling is ever needed; **LiteFS** is the option for read-scaling while keeping SQLite. **Litestream** = backup-to-object-storage (separate from LiteFS).
