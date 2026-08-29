# Spec: Login and Logout

## Overview

Make `/login` actually sign somebody in, and make `/logout` sign them out.
Today `/login` is GET-only — `login.html` already POSTs, so submitting it
returns **405** — and `/logout` returns the placeholder string
`"Logout — coming in Step 3"`.

This step adds the POST branch to `/login`: look the email up in the
`users` table, verify the submitted password against the stored Werkzeug
hash, and on success record the user's id in Flask's `session`. `/logout`
clears that session. The navbar becomes session-aware, so a signed-in user
can see they are signed in and has somewhere to click to leave.

This is the second half of authentication and the first code in Spendly to
use `session` at all, which is why `app.secret_key` arrives here. Step 2
was deliberately built to need neither.

## Depends on

- **Step 1 — SQLite database setup.** Complete on `main`. `get_db()`
  returns rows with `sqlite3.Row`, and `users.password_hash` already holds
  a Werkzeug hash for both the seeded demo user and anyone registered.
- **Step 2 — Registration. Complete, but only on the
  `feature/registration` branch — it is not on `main` yet.** This step
  builds directly on Step 2's work: `create_user()` in `database/db.py`,
  the `?registered=1` success banner in `login.html`, and the
  `.auth-success` CSS rule. Merge Step 2 into `main` and rebase this
  branch onto it before implementing, or the changes below will conflict
  and there will be no way to register an account to log in with.

The seeded demo account (`demo@spendly.com` / `demo123`) means login can
be tested even before any account is registered by hand.

## Routes

- `GET, POST /login` — **modify existing.** GET renders the form as it
  does now, including Step 2's `?registered=1` banner. POST verifies the
  credentials, sets `session["user_id"]`, and redirects to `/profile`. On
  failure it re-renders `login.html` with an `error` message and HTTP
  **401** — not 400 — because the submission was well-formed and the
  credentials were what was wrong. Access: public.
- `GET /logout` — **replace placeholder.** Clears the session and
  redirects to the landing page. Access: public; hitting it while signed
  out is a no-op redirect, not an error.

No other routes change. `/profile` keeps its Step 4 placeholder string —
this step only needs somewhere to land after a successful sign-in.

## Database changes

**No database changes.** The `users` table from Step 1 has every column
this step reads, and `email TEXT NOT NULL UNIQUE` guarantees the lookup
returns at most one row.

One new helper is added to `database/db.py` — it reads the existing
schema, it does not alter it:

- `get_user_by_email(email)` — returns the `sqlite3.Row` for that address,
  or `None` when there is no such user. Parameterised query; does no
  password checking of its own.

## Templates

**Create:** none.

**Modify:**

- `templates/login.html` — re-fill the email field with the value just
  submitted (`value="{{ email or '' }}"`) so a failed attempt does not
  force a retype. Never re-fill the password. The `{% if error %}` block
  it already has needs no change.
- `templates/base.html` — make the navbar session-aware: show "Sign in"
  and "Get started" to a signed-out visitor as it does now, and the user's
  name plus a "Log out" link to a signed-in one. `session` is available in
  Jinja without being passed in, so no route has to hand it over.

## Files to change

- `app.py` — `app.secret_key`, `methods=["GET", "POST"]` on `/login`, the
  verification logic, the real `/logout` body, and the imports they need
  (`os`, `session`, `check_password_hash`, `get_user_by_email`).
- `database/db.py` — add `get_user_by_email()`.
- `templates/login.html` — sticky email field.
- `templates/base.html` — session-aware navbar.
- `static/css/style.css` — style the signed-in navbar items under the
  existing **Navbar** banner.

## Files to create

- `tests/test_login.py` — login and logout coverage, using the `client`
  and `temp_db` fixtures already in `tests/conftest.py`. (That file
  arrives with Step 2; see **Depends on**.)

## New dependencies

**No new dependencies.** `session` is part of Flask, `check_password_hash`
is the Werkzeug counterpart to the `generate_password_hash` already in
use, and `os` is stdlib. Do not add Flask-Login.

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` and raw SQL only.
- Parameterised queries only. Never build SQL with string formatting or
  f-strings.
- Verify passwords with `werkzeug.security.check_password_hash`. Never
  compare hashes with `==`, and never re-hash the submitted password to
  compare the results — two hashes of the same password differ by salt.
  Do not add bcrypt or passlib.
- Never log, flash, or render the submitted password.
- Use CSS variables — never hardcode hex values. The signed-in navbar
  needs no new custom properties; `--ink-muted` and `--accent` cover it.
- All templates extend `base.html`.
- **Do not add a `url_for()` call to `base.html` for an endpoint that does
  not exist** — every page inherits it, so a `BuildError` there takes down
  the whole site. `url_for('logout')` is safe: that endpoint is registered
  today and stays registered.
- `app.secret_key` must come from the environment with a development
  fallback: `os.environ.get("SPENDLY_SECRET_KEY", "<dev-only literal>")`.
  A hardcoded key is acceptable for this teaching scaffold, and only
  because the fallback is obviously named as dev-only — a real deployment
  sets the variable. Do not add `python-dotenv` to read a `.env`.
- Store only `session["user_id"]` as the source of truth. A display name
  in the session is fine for the navbar, but never trust the session for
  anything the database should be asked about.
- **Give one generic error for every failed attempt** — "Incorrect email
  or password." Distinct messages for "no such user" and "wrong password"
  tell an attacker which addresses are registered.
- Normalise the submitted email with `.strip().lower()` before the lookup,
  exactly as Step 2 does before the insert. Without it, an account
  registered as `demo@spendly.com` could not be signed into by typing
  `Demo@Spendly.com`. Do not strip the password — spaces are legitimate
  password characters.
- Call `session.clear()` in `/logout`, not `session.pop("user_id")`, so
  nothing a later step adds to the session survives a sign-out.
- Redirect after a successful login rather than rendering — a refresh on
  a rendered POST re-submits the credentials.
- `/logout` stays a GET so the navbar link works, matching the existing
  placeholder route. A production app would make it a POST with a CSRF
  token; WTForms is deliberately excluded here, so that is out of scope.

## Definition of done

- [ ] `python app.py` starts with no errors and `/login` renders as before.
- [ ] Submitting the login form no longer returns 405.
- [ ] Signing in as `demo@spendly.com` / `demo123` redirects to `/profile`
      and shows the Step 4 placeholder string.
- [ ] `DEMO@Spendly.com ` (mixed case, trailing space) signs in too.
- [ ] A wrong password re-renders the form with "Incorrect email or
      password." and HTTP 401, and does not sign the user in.
- [ ] An unregistered email gives that same message — the two failures are
      indistinguishable in wording and in status code.
- [ ] After a failed attempt the email field still holds what was typed
      and the password field is empty.
- [ ] While signed in, every page's navbar shows the user's name and a
      "Log out" link instead of "Sign in" / "Get started".
- [ ] Clicking "Log out" returns to the landing page, and the navbar is
      back to "Sign in" / "Get started".
- [ ] Visiting `/logout` while already signed out redirects to the landing
      page without erroring.
- [ ] An account registered through `/register` can immediately sign in
      with the password it was created with — Step 2 and Step 3 agree on
      hashing.
- [ ] No hex literal was added to `style.css`, and every page still loads,
      confirming `base.html` was not broken.
- [ ] `pytest` passes, including the Step 1 and Step 2 tests.
