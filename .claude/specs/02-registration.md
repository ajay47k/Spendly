# Spec: Registration

## Overview

Make `/register` actually create an account. Today the route is GET-only,
so the form in `register.html` — which already POSTs — returns **405**.
This step adds the POST branch: validate the submitted name, email and
password, hash the password with Werkzeug, insert a row into the `users`
table built in Step 1, and send the new user on to the sign-in page.

This is the first half of authentication. Registration only *creates* the
account; nothing here logs anybody in. Sessions, `secret_key`, `/login`
and `/logout` all belong to Step 3, and this step is deliberately built so
it needs none of them.

## Depends on

- **Step 1 — SQLite database setup.** Complete. `get_db()`, `init_db()`
  and `seed_db()` exist, and the `users` table already has the
  `email TEXT NOT NULL UNIQUE` constraint this step relies on.

## Routes

- `GET, POST /register` — **modify existing.** GET renders the form as it
  does now. POST validates, creates the user, and redirects to
  `/login?registered=1`. On failure it re-renders `register.html` with an
  `error` message and HTTP **400**, so a bad submission is distinguishable
  from a fresh page load. Access: public.

No other routes change. `/login` stays GET-only until Step 3.

## Database changes

**No database changes.** The `users` table from Step 1 already has every
column this step writes (`name`, `email`, `password_hash`, `created_at`)
and its `UNIQUE` constraint on `email` is what enforces "one account per
address".

One new helper is added to `database/db.py` — it uses the existing schema,
it does not alter it:

- `create_user(name, email, password)` — hashes `password` with
  `generate_password_hash`, inserts the row, returns the new `id`.
  Lets `sqlite3.IntegrityError` propagate when the email is taken.

## Templates

**Create:** none.

**Modify:**

- `templates/register.html` — re-fill `name` and `email` with the values
  the user just submitted (`value="{{ name or '' }}"`) so a rejected
  submission does not force a full retype. The `{% if error %}` block it
  already has needs no change.
- `templates/login.html` — render a success banner when
  `request.args.get('registered')` is set, so a redirected user is told
  the account was created. This is the only reason Step 2 touches the
  login template.

## Files to change

- `app.py` — add `methods=["GET", "POST"]` to `/register`, the validation
  and creation logic, and the imports it needs (`request`, `redirect`,
  `url_for`, `sqlite3`, `create_user`).
- `database/db.py` — add `create_user()`.
- `templates/register.html` — sticky `name` and `email` fields.
- `templates/login.html` — success banner for `?registered=1`.
- `static/css/style.css` — add `.auth-success` under the existing
  **Auth pages** banner, mirroring `.auth-error`.

## Files to create

None.

## New dependencies

**No new dependencies.** `werkzeug.security` and stdlib `sqlite3` are
already in use.

## Rules for implementation

- No SQLAlchemy or ORMs — raw `sqlite3` and raw SQL only.
- Parameterised queries only. Never build SQL with string formatting or
  f-strings.
- Passwords hashed with `werkzeug.security.generate_password_hash`. Never
  store or log the plaintext password. Do not add bcrypt or passlib.
- Use CSS variables — never hardcode hex values. `.auth-success` uses
  `--accent-light` for background and `--accent` for text; no new
  custom properties are needed.
- All templates extend `base.html`.
- **Do not add `app.secret_key`, `session`, or `flash()`.** Those arrive
  in Step 3. Registration feedback travels as the `?registered=1` query
  parameter precisely so this step stays session-free.
- **Do not add a `url_for()` call to `base.html`** — every page inherits
  it, so a `BuildError` there takes down the whole site.
- Let the `UNIQUE` constraint be the authority on duplicate emails: catch
  `sqlite3.IntegrityError` around the insert rather than doing a
  "does this email exist?" SELECT first. A pre-check has a race between
  the read and the write; the constraint does not.
- Normalise the email before inserting — `.strip().lower()` — so
  `Demo@Spendly.com` cannot become a second account alongside
  `demo@spendly.com`. Strip whitespace from `name` too.
- Validation rules, all server-side (the HTML `required` attribute is a
  convenience, not a guarantee):
  - `name` — non-empty after stripping
  - `email` — non-empty, and contains an `@` with text either side
  - `password` — at least 8 characters, matching the form's own
    "Min. 8 characters" placeholder
- Show one error at a time in the existing `.auth-error` block; the
  message should say what to fix, e.g. "Password must be at least 8
  characters."

## Definition of done

- [ ] `python app.py` starts with no errors and `/register` renders as before.
- [ ] Submitting the registration form no longer returns 405.
- [ ] A valid submission lands on `/login?registered=1` with a visible
      "Account created — sign in below" banner.
- [ ] The new user is in the database: `SELECT email, password_hash FROM users`
      shows the row, and `password_hash` is a Werkzeug hash — not the
      plaintext password.
- [ ] Registering `demo@spendly.com` again re-renders the form with an
      "email already registered" error and creates no second row.
- [ ] `DEMO@Spendly.com ` (mixed case, trailing space) is rejected as a
      duplicate too.
- [ ] A 7-character password is rejected with the length error, and no
      user row is created.
- [ ] An empty name (spaces only) is rejected, and no user row is created.
- [ ] After a rejected submission, the name and email fields still hold
      what was typed.
- [ ] The error and success banners use the CSS variables — no new hex
      literals appear in `style.css`.
- [ ] Every page still loads, confirming `base.html` was not broken.
