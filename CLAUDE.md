# Personal Website — Flask (Python)

Louis Lizzadro's personal site — a standalone Flask app, **live at https://lllizzadro.fly.dev**. (Built to learn web dev; a retired Go/Gin twin is archived — work only here.)

## Working with Louis
- **Hands-on learner.** Explain the concept and what's needed, let him write the code, then review and explain mistakes. Write code directly only to demo a brand-new concept or when he's stuck after trying. He validates the UI himself — don't generate screenshots unless asked.

## Stack & conventions
- **Flask + Jinja**, templates in `templates/`; `base.html` is the layout (`{% extends "base.html" %}` + `{% block content %}`).
- **Tailwind via CDN** — no build step; `tailwind.config` inline in `base.html`'s `<head>`. Bespoke CSS (things utilities do poorly: background layer, `.premium-glass`, nav underline, heading font) lives in `static/css/style.css`, linked via `url_for`. Still no-build; if outgrown, next step is a Tailwind build (PostCSS) for purge/`@apply`, not hand-CSS.
- **SQLite** (stdlib `sqlite3`): `get_db()` opens lazily per request, stores the connection on Flask `g`, sets `row_factory = sqlite3.Row`; `@app.teardown_appcontext` (`close_db`) closes it — no per-route close. Path = `os.environ.get('DATABASE_PATH', 'guestbook.db')`. `init_db()` runs at module level with its **own** `sqlite3.connect` (no app context outside a request) — module-level so it works under gunicorn too.
- **Always parameterize queries** (`?` placeholders) — never string-format user input.
- **Secrets via env**: `SECRET_KEY = os.environ.get('SECRET_KEY', 'dev')` signs the session cookie / `flash()`. `'dev'` is local-only; prod sets a real key via Fly secrets.
- **POST/Redirect/GET** for state-changing forms. `add_message()` validates server-side (strip, reject empty, name ≤ 50 / message ≤ 1000), reports failures with `flash()` + redirect; `base.html` renders flashes above `{% block content %}`.
- **Client JS** in `static/js/` via `url_for`: `localtime.js` (local timestamps), `nav.js` (mobile menu).

## Theming & UI
- **Accent** `purple-600`; **gray base** `neutral` (not `slate` — too blue under purple). Page-title `h1`s are `purple-600` (exception: home hero `h1` is `neutral-100` with only "Louis." in `purple-600`).
- **Fonts**: Inter (body) + Space Mono (headings/brand/nav), via Google Fonts. `tailwind.config` sets `sans`=Inter, `mono`=Space Mono; an `h1,h2,h3` rule in `style.css` applies Space Mono; brand + nav use `font-mono`.
- **Dark-only** — renders dark unconditionally: no theme toggle, no `darkMode` config, no `dark:` variants (all flattened to defaults like `bg-neutral-900`). To re-add light mode: reinstate `darkMode:'class'` + `dark:` variants.
- **Glass UI — two treatments:** (a) **bars & form inputs**: light utility glass `bg-white/5 backdrop-blur-sm backdrop-saturate-150 border border-white/20` (nav `border-b`, footer `border-t`). (b) **panels & cards** (project/guestbook cards, résumé sheet): the **`.premium-glass`** class in `style.css` — near-black translucent base + white→purple highlight gradient + inset top-highlight + drop shadow + low blur + a `::before` purple edge sheen; `.premium-glass > *` lifts content above the sheen; add **`.interactive`** for hover lift. Hard-won rules: (1) background lives **only on `body`** — panels are translucent so it shows through; never repeat it on `nav`/`section` (each re-anchors → muddy). (2) `backdrop-saturate` is essential — plain blur desaturates/looks muted; saturate re-pops color. Dials: blur=frostiness, fill opacity=clarity, border=edge. (3) **don't double-layer** — the mobile menu is *inside* `nav`, so it has no bg of its own.
- **Background** (`style.css`): cosmic image `static/images/purpleCosmic.jpg` on a **`body::before` fixed layer** (`position:fixed; top/left:0; width:100%; height:100lvh` w/ `100vh` fallback; `z-index:-1; background-size:cover`), `#080911` base/fallback. Referenced with a relative `url(../images/...)` (external CSS resolves URLs to itself). Commented purple `radial-gradient` glow layers sit there for optional re-enable. **Mobile gotchas (don't regress):** `background-attachment: fixed` is buggy on mobile → use the fixed pseudo-element instead; size with **`100lvh`** not `100vh`/`inset:0` (the address bar showing/hiding changes viewport height and makes a `100vh` layer **jump mid-scroll**). **Optimize images** — PNG → JPEG/WebP (`sips -s format jpeg -s formatOptions 82` took 1.6 MB → 176 KB); never ship big PNGs for photographic art.
- **Per-page content width**: `base.html` defines `{% block main_width %}max-w-3xl{% endblock %}` once (nav container) and reuses it on `<main>` + footer via `{{ self.main_width() }}` (a block can only be *defined* once; `self.` re-renders it). Home overrides to `max-w-5xl` (two-column hero); others default `max-w-3xl`. Keeps nav/content/footer edges aligned.
- **Nav** (`base.html`): brand is `</>` glyph + name. Inline links on `md+` (`hidden md:flex`); hamburger (`#nav-toggle`, `md:hidden`) opens the in-flow `#mobile-menu` — `nav.js` toggles `.open`, which animates `max-height` + `opacity` + `padding` in `style.css` (NOT `display:none` — can't transition). Collapsed = `max-height:0` **with padding zeroed** (padding can't compress under `max-height`, so it lives in `.open` to avoid a leftover gap). Active page: `aria-current="page"` (Jinja exact `==`) → CSS colors it (`nav a[aria-current="page"]`) and desktop `.nav-link`s get a center-out sliding underline (`::after`, also on `:hover`); mobile links get the color only.
- **Timestamps**: stored UTC, shown local — `<time>` carries ISO-UTC `datetime` (`| isodate`) with `| prettydate` fallback; `localtime.js` rewrites via `toLocaleString`.

## Run
```
pip install -r requirements.txt
python app.py        # http://localhost:5000
```
LAN/phone testing: `python -m flask --app app run --host=0.0.0.0 --port=5000` → `http://<computer-LAN-IP>:5000`.

## Deployment — Fly.io (live)
- **App `lllizzadro`** → https://lllizzadro.fly.dev (region `ord`). Docker (`python:3.13-slim`, gunicorn `:8080`) + `fly.toml` + `.dockerignore`.
- **Persistent SQLite**: 1 GB volume `data` at `/data`; `DATABASE_PATH=/data/guestbook.db` survives redeploys. **Single machine only** — a volume binds to one machine; scaling out diverges the data.
- **CI/CD** (`.github/workflows/fly-deploy.yml`): deploys on **push to `main`**. Flow: work on `dev` → PR → merge to `main` = production. Needs the `FLY_API_TOKEN` Actions secret (`fly tokens create deploy`).
- **Ops**: `fly status` / `fly logs` / `fly open`; `fly ssh console` (only `/data` persists); `fly ssh sftp` for the DB. Manual deploy needs flyctl (Windows: `iwr https://fly.io/install.ps1 -useb | iex`).

## Status
- ✅ **Home** — two-column hero (`max-w-5xl`): left = heading + social icons (SVGs use `fill`/`stroke="currentColor"` to inherit hover color); right = a `.premium-glass` **"Currently" panel** (status dot + `<dl>` + skill pills). Below: **case-study project cards** from `PROJECTS` (each: `name`/`description`/`tech` list/optional `live`/`source`) rendering tech pills + conditional Visit Site / Source links (`{% if %}` omits missing). **Tech pills are category color-coded** (purple=languages, cyan=frameworks, amber=infra) via a `{% if t in [...] %}` lookup in the loop; new techs default to cyan unless added to the lists in `index.html`.
- ✅ **Guestbook** — SQLite, `.premium-glass` message cards + utility-glass inputs, local-time timestamps, validation + flash feedback.
- ✅ **Resume** — themed page + "Download PDF" (`static/resume.pdf`); phone omitted (public).
- ✅ Dark-only theming, glass UI, cosmic background, animated hamburger nav, Fly.io push-to-deploy CI/CD.

## Ideas / deferred
- **Curated-links wall** (preferred guestbook glow-up): visitors submit links (URL + title + blurb) → curated feed. Reuse form/SQLite/PRG/validation; **validate URL scheme (http/https allow-list)**; open in new tab with `rel="noopener noreferrer"`; pairs with CSRF (public write endpoint).
- **New pages**: `/now`, `/uses`, bookmarks, blog.
- **Security/polish**: CSRF (Flask-WTF + `{{ csrf_token() }}`); style the flash banner (currently unstyled `flash-messages`/`flash-message`); guestbook empty-state + message count (revisit count with more entries).
- **DB**: stay on SQLite; revisit SQLAlchemy + Postgres for a relation-heavy feature (e.g. blog); LiteFS (read-scaling) / Litestream (backups) only if needed.
- **Background motion**: optional subtle drifting glow / sparse animated stars over the static image — keep subtle + gate on `prefers-reduced-motion`; remember anything moving under the glass re-blurs every frame (backdrop-filter cost). A full WebGL nebula shader was prototyped and rejected (low fidelity vs a static image).
