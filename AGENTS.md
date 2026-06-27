# Personal Website — Flask (Python)

Louis Lizzadro's personal site — a standalone Flask app, **live at https://lllizzadro.fly.dev**. (Originally built alongside a Go/Gin twin to learn web dev; Gin is retired/archived — work only here now.)

## Working with Louis
- **Hands-on learner.** Explain the concept and what's needed, let him write the code, then review and explain any mistakes. Write code directly only to demonstrate a brand-new concept or when he's stuck after trying. He validates the UI himself — don't generate screenshots unless asked.

## Stack & conventions
- **Flask + Jinja**, templates in `templates/`; `base.html` is the layout (`{% extends "base.html" %}` + `{% block content %}`).
- **Tailwind via CDN** — no build step; config set inline in `base.html`'s `<head>` (`tailwind.config`).
- **SQLite** (stdlib `sqlite3`): `get_db()` opens lazily per request, stores the connection on Flask `g`, sets `row_factory = sqlite3.Row`; a `@app.teardown_appcontext` (`close_db`) closes it — no per-route close. DB path = `os.environ.get('DATABASE_PATH', 'guestbook.db')`. `init_db()` runs at module level with its **own** `sqlite3.connect` (not `get_db()` — there's no app context outside a request); module-level so it also works under gunicorn.
- **Always parameterize queries** (`?` placeholders) — never string-format user input.
- **Secrets via env**: `SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')` signs the session cookie / powers `flash()`. `'dev'` is local-only; prod sets a real key via Fly secrets.
- **POST/Redirect/GET** for state-changing forms. `add_message()` validates server-side (strip, reject empty, name ≤ 50 / message ≤ 1000) and reports failures with `flash()` + redirect; `base.html` renders flashes above `{% block content %}`.
- **Client JS** in `static/js/`, loaded via `url_for('static', ...)`: `theme.js` (dark toggle), `localtime.js` (local timestamps), `nav.js` (mobile menu toggle).

## Theming & UI
- **Accent** `purple-600`; **gray base** `neutral` (not `slate` — too blue under purple). Page-title `h1`s are `purple-600`.
- **Fonts** (Google Fonts): Inter (body) + Space Mono (headings, brand, nav). `tailwind.config fontFamily` sets `sans`=Inter, `mono`=Space Mono; a base `<style> h1,h2,h3` rule applies Space Mono to headings; brand + nav links use the `font-mono` class.
- **Dark mode**: Tailwind `darkMode: 'class'`. An inline `<head>` script applies the saved/system theme before paint (no flash); `theme.js` toggles the `dark` class on `<html>` and saves to `localStorage`; sun/moon icons swap via `dark:hidden` / `hidden dark:inline`.
  - Dark-mode gotchas: shadow-based hover is invisible on dark, so cards use `dark:hover:bg-neutral-700`. A plain `hover:` color can also lose to a `dark:` base style on specificity/source-order, so hover colors that must show in dark need a `dark:hover:` twin (cards use `hover:border-purple-400 dark:hover:border-purple-400`).
- **Nav** (`base.html`): responsive — inline links on `md+` (`hidden md:flex`); a hamburger (`#nav-toggle`, `md:hidden`) opens the `#mobile-menu` dropdown (`nav.js` toggles `hidden`); theme toggle always visible. Active page is highlighted purple via `{% if request.path == '/...' %}text-purple-600{% endif %}` on each link (exact `==` — `in`/`startswith` would mis-highlight).
- **Timestamps**: stored UTC, shown in each visitor's local time — `<time>` carries an ISO-UTC `datetime` (`| isodate` filter) with a `| prettydate` fallback; `localtime.js` rewrites it via `toLocaleString`.

## Run
```
pip install -r requirements.txt
python app.py        # http://localhost:5000
```
LAN testing (view on phone): `python -m flask --app app run --host=0.0.0.0 --port=5000` → `http://<computer-LAN-IP>:5000`.

## Deployment — Fly.io (live)
- **App `lllizzadro`** → https://lllizzadro.fly.dev (region `ord`). Docker (`python:3.13-slim`, gunicorn on `:8080`) + `fly.toml` + `.dockerignore`.
- **Persistent SQLite**: 1 GB volume `data` mounted at `/data`; `DATABASE_PATH=/data/guestbook.db` keeps data across redeploys. **Single machine only** — a volume binds to one machine; scaling out would diverge the SQLite data.
- **CI/CD**: `.github/workflows/fly-deploy.yml` deploys on **push to `main`**. Flow: work on `dev` → PR → **merge to `main` = production**. Requires the `FLY_API_TOKEN` GitHub Actions secret (created via `fly tokens create deploy`).
- **Ops**: `fly status` / `fly logs` / `fly open`; `fly ssh console` (only `/data` persists); `fly ssh sftp` to pull/push the DB. Manual deploy needs flyctl (Windows install: `iwr https://fly.io/install.ps1 -useb | iex`).

## Status
- ✅ **Home** — bio + project cards
- ✅ **Guestbook** — SQLite, card layout, local-time timestamps, server-side validation + flash feedback
- ✅ **Resume** — themed HTML page + "Download PDF" button (`static/resume.pdf`); phone number omitted (public page)
- ✅ Theming, dark mode, responsive hamburger nav, and Fly.io deploy with push-to-deploy CI/CD all complete

## Ideas / deferred
- **Curated-links wall** (preferred guestbook glow-up): visitors submit links (URL + title + blurb) → a growing curated feed. Reuse the form/SQLite/PRG/validation infra; new/extended table; **validate URL scheme (http/https allow-list)**; open links in a new tab with `rel="noopener noreferrer"`; pairs with CSRF since it's a public write endpoint.
- **New pages**: `/now`, `/uses` (best effort/reward), bookmarks, blog.
- **Security/polish**: CSRF (Flask-WTF + `{{ csrf_token() }}`); style the flash banner (currently unstyled `flash-messages`/`flash-message` classes); guestbook empty-state ("be the first").
- **DB**: stay on SQLite for now; revisit SQLAlchemy + Postgres for a relation-heavy feature (e.g. blog); LiteFS (read-scaling) / Litestream (backups) only if ever needed.
