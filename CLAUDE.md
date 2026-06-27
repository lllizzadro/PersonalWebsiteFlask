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
- **Client JS** in `static/js/`, loaded via `url_for('static', ...)`: `localtime.js` (local timestamps), `nav.js` (mobile menu toggle).

## Theming & UI
- **Accent** `purple-600`; **gray base** `neutral` (not `slate` — too blue under purple). Page-title `h1`s are `purple-600` (exception: the home hero `h1` is `neutral-100` with only the accent word "Louis." in `purple-600`, per the mockup).
- **Fonts** (Google Fonts): Inter (body) + Space Mono (headings, brand, nav). `tailwind.config fontFamily` sets `sans`=Inter, `mono`=Space Mono; a base `<style> h1,h2,h3` rule applies Space Mono to headings; brand + nav links use the `font-mono` class.
- **Dark-only theme** (light mode removed 2026-06-17): the site renders dark unconditionally — no theme toggle, no `theme.js`, no `darkMode` config, no inline theme script. All former `dark:` variants were flattened to plain defaults (e.g. `bg-neutral-900`, `text-neutral-400`). Cards: `bg-neutral-800`, `border-neutral-700`, `hover:bg-neutral-700`, `hover:border-purple-400`. (If light mode is ever wanted again, reintroduce `darkMode: 'class'` + the `dark:` variants.)
- **Glass UI** (2026-06-17 redesign): nav, footer, mobile menu, and all cards/inputs share one frosted-glass recipe — `bg-white/5 backdrop-blur-sm backdrop-saturate-150 border border-white/20` (cards add `shadow-xl shadow-purple-950/30 hover:bg-white/10 hover:border-purple-400/60`). Three principles learned the hard way: (1) the page background lives **only on `body`** (one coordinate system) — panels are translucent so it shows through; do NOT repeat the background on `nav`/`section` (each element re-anchors its own copy → muddy). (2) `backdrop-saturate-150` is essential — plain `backdrop-blur` averages/desaturates what's behind it and looks muted/frosty; saturate re-pops the color for a "clearer glass" look. Blur amount = frostiness, fill opacity = clarity, border brightness = edge definition. (3) **Don't double-layer**: the mobile menu sits *inside* `nav`, so it has **no** background of its own (the nav's glass shows through) — adding `bg-white/5` to it too would stack to ~2× lighter. The mobile menu is **in-flow** (pushes content down via `border-t`), not `absolute` — an absolute overlay was unreadable over page text.
- **Background**: cosmic image `static/images/purpleCosmic.jpg` on `body` via `background-size: cover; background-position: center; background-attachment: fixed`, with `#080911` as the base/fallback color. Two purple `radial-gradient` glow layers are kept **commented** in the `<style>` block for optional re-enable. **Optimize images** — the source was a 1.6 MB PNG; converted to a 176 KB JPEG with `sips -s format jpeg -s formatOptions 82` (~90% smaller, no visible loss). Prefer JPEG/WebP over PNG for photographic/gradient art. Reference it via `{{ url_for('static', ...) }}` *inside* the `<style>` block (works because `base.html` is a Jinja template) — not a relative `../static` path.
- **Per-page content width**: `base.html` defines `{% block main_width %}max-w-3xl{% endblock %}` once (on the nav container) and reuses its value on `<main>` and the footer via `{{ self.main_width() }}` (Jinja renders a block's value in multiple spots this way — a block name can only be *defined* once). A page sets its width with one line: the home page overrides to `max-w-5xl` (wider, for the two-column hero); other pages default to `max-w-3xl`. Keeps nav / content / footer edges aligned per page.
- **Nav** (`base.html`): brand is a `</>` glyph (`<span class="text-purple-600">&lt;/&gt;</span>`) + name. Responsive — inline links on `md+` (`hidden md:flex`); a hamburger (`#nav-toggle`, `md:hidden`) opens the in-flow `#mobile-menu` (`nav.js` toggles `hidden`). Active page is highlighted purple via `{% if request.path == '/...' %}text-purple-600{% endif %}` on each link (exact `==` — `in`/`startswith` would mis-highlight).
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
- ✅ **Home** — two-column hero (`max-w-5xl`): heading + social icon row (GitHub/LinkedIn/email SVGs using `fill`/`stroke="currentColor"` so they inherit the link's hover color) on the left; a glass **code-window** card on the right (`main.py` title bar + a Python snippet syntax-highlighted with hand-colored `<span>`s — no JS highlighter — in a vaporwave neon palette via `text-[#hex]` arbitrary values). `<pre>` content is kept flush-left in the file since its whitespace renders literally. Below: project cards from the `PROJECTS` list.
- ✅ **Guestbook** — SQLite, glass card layout, local-time timestamps, server-side validation + flash feedback
- ✅ **Resume** — themed HTML page + "Download PDF" button (`static/resume.pdf`); phone number omitted (public page)
- ✅ Theming (dark-only) + glass UI redesign, cosmic background, responsive hamburger nav, and Fly.io deploy with push-to-deploy CI/CD all complete

## Ideas / deferred
- **Curated-links wall** (preferred guestbook glow-up): visitors submit links (URL + title + blurb) → a growing curated feed. Reuse the form/SQLite/PRG/validation infra; new/extended table; **validate URL scheme (http/https allow-list)**; open links in a new tab with `rel="noopener noreferrer"`; pairs with CSRF since it's a public write endpoint.
- **New pages**: `/now`, `/uses` (best effort/reward), bookmarks, blog.
- **Security/polish**: CSRF (Flask-WTF + `{{ csrf_token() }}`); style the flash banner (currently unstyled `flash-messages`/`flash-message` classes); guestbook empty-state ("be the first").
- **DB**: stay on SQLite for now; revisit SQLAlchemy + Postgres for a relation-heavy feature (e.g. blog); LiteFS (read-scaling) / Litestream (backups) only if ever needed.
