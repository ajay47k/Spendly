# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

**Spendly** — a personal expense tracker (rupee-denominated). Critically, this is a **teaching scaffold, not a half-finished app**: the front end is complete and polished, while the back end is deliberately unwritten and meant to be built in 9 numbered steps.

Do not "fix" the unimplemented parts unless asked. The placeholder route bodies (`"Add expense — coming in Step 7"`) and the comments-only `database/db.py` are the assignment, not bugs. Step numbers appear directly in the source and are the roadmap:

| Step | Work |
|---|---|
| 1 | `database/db.py` — schema and connection |
| 2–3 | Registration, login, sessions, logout |
| 4 | Profile page |
| 7–9 | Expense add / edit / delete |

When implementing a step, replace the placeholder in `app.py` and remove the "coming in Step N" string.

## Commands

```powershell
.\venv\Scripts\Activate.ps1        # PowerShell
```
```bash
source venv/Scripts/activate       # Git Bash
```

```bash
pip install -r requirements.txt    # exact pins; see Stack below
python app.py                      # dev server, http://127.0.0.1:5001
```

**The port is 5001, not Flask's default 5000** (set in the `app.run()` call at the bottom of `app.py`). Debug mode and the auto-reloader are on, so template and Python edits reload without a restart.

Testing (pytest + pytest-flask):

```bash
pytest                             # all
pytest tests/test_register.py      # one file
pytest tests/test_register.py::test_password_is_hashed       # one test
pytest -k "login"                  # by name pattern
```

`tests/conftest.py` already provides the two fixtures every later step needs: `temp_db` repoints `db.DB_PATH` at a `tmp_path` database, and `app` returns the Flask instance wired to it — which is what makes pytest-flask's `client` fixture work. Take `client` or `temp_db` as an argument; do not write your own.

`app` imports `app.py` *inside* the fixture, not at module scope. `app.py` calls `init_db()` and `seed_db()` at import time, so importing it before `temp_db` has patched `DB_PATH` would create and seed the real `expense_tracker.db` as a side effect of running the tests.

## Architecture

**Server-rendered Flask with no build step, no ORM, and no Node.** All four templates extend `base.html`, which owns the navbar, footer, font loading, and the `content` / `title` / `head` / `scripts` blocks. Page templates define blocks only.

`database/db.py` is a written contract, currently comments only. It must expose:

- `get_db()` — SQLite connection with `row_factory` set and foreign keys enabled
- `init_db()` — `CREATE TABLE IF NOT EXISTS` for all tables
- `seed_db()` — sample development data

Use the stdlib `sqlite3` and raw SQL. **Adding SQLAlchemy, Alembic, Flask-Login, or WTForms defeats the exercise** — these are omitted on purpose. Name the database file `expense_tracker.db`; `.gitignore` already excludes exactly that name.

`static/css/style.css` (530 lines) is organized under comment banners — `Variables`, `Reset`, `Navbar`, `Hero`, `Mock card`, `Buttons`, `Features section`, `CTA section`, `Auth pages`, `Footer`, `Responsive`. Add new rules under the matching banner. Colors, fonts, radii, and widths are CSS custom properties on `:root` (`--ink`, `--paper`, `--accent`, `--font-display`, `--radius-md`, …); use the tokens rather than hardcoding values.

## Non-obvious constraints

**The auth forms are wired to routes that reject them.** `login.html` and `register.html` both `POST`, but `/login` and `/register` are GET-only, so submitting returns **405**. Adding `methods=["GET", "POST"]` and the POST branch is part of Steps 2–3.

**Never reference a non-existent endpoint with `url_for()` in `base.html`.** Because every page inherits it, a `url_for('terms')` for an unregistered endpoint raises `BuildError` and takes down the *entire site*, not just that link. Use a literal `href="/terms"` until the route exists. The footer's Terms and Privacy Policy links are currently literal hrefs for this reason, and both 404 until routes are added.

**Werkzeug is pinned explicitly in `requirements.txt` even though Flask already depends on it.** That signals password hashing should use `werkzeug.security.generate_password_hash` / `check_password_hash` — do not add bcrypt or passlib.

**`Flask.__version__` is deprecated and `werkzeug.__version__` no longer exists.** Use `importlib.metadata.version("flask")` for runtime version checks.

## Stack

Python 3.14 · Flask 3.1.3 · Werkzeug 3.1.6 · Jinja2 · SQLite (stdlib `sqlite3`) · pytest 8.3.5 · pytest-flask 1.3.0 · vanilla CSS and JS · DM Serif Display + DM Sans via Google Fonts.

Remote: `https://github.com/ajay47k/Spendly.git` (branch `main`).
