# Personal Website — Flask (Python)

A personal website built and maintained by **Louis Lizzadro**. It was originally built in parallel with a Go/Gin twin to learn web dev, but as of 2026-06-14 **this Flask version is the single canonical site** — the Gin version has been retired (archived for reference, no longer maintained). Work only happens here now.

## About Louis
- Software developer learning web dev. GitHub: `lllizzadro`.
- **Hands-on learner — this matters.** Guide him to write the code himself: explain the concept and what's needed, let him implement it, then review what he wrote and explain any mistakes. Only write code directly when demonstrating a brand-new concept for the first time, or when he's stuck after trying. (He also validates the UI himself — don't generate screenshots unless asked.)

## Stack & conventions
- **Flask + Jinja** templates in `templates/`. `base.html` is the layout; pages use `{% extends "base.html" %}` + `{% block content %}`.
- **Tailwind CSS via CDN** (`<script src="https://cdn.tailwindcss.com">`) — no build step. Config is set inline in `base.html`'s `<head>` via `tailwind.config`.
- **SQLite** via stdlib `sqlite3`. Open a fresh connection per request with `get_db()` (which sets `row_factory = sqlite3.Row` for named columns). `init_db()` runs once at module level (not in `__main__`, so it also works under gunicorn).
- **Always use parameterized queries** (`?` placeholders) — never string-format user input (SQL injection).
- State-changing forms use the **POST/Redirect/GET** pattern.
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

## Status
- ✅ Home (`/`) — bio + projects list
- ✅ Guestbook (`/guestbook`) — SQLite-backed, form + POST/Redirect/GET, card layout, local-time timestamps
- ✅ Styling pass complete — purple/neutral theme, dark mode w/ toggle, Inter/Space Mono fonts, responsive foundation
- ⏭️ Possible next: more pages (now/bookmarks/blog/etc.) or deployment. When the nav outgrows the space (more links), add a responsive hamburger menu — deferred until then.
