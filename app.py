import sqlite3

from flask import Flask, redirect, render_template, request, url_for

from database.db import create_user, get_db, init_db, seed_db

app = Flask(__name__)

# Make sure the schema and demo data exist before any route runs. Both calls
# are idempotent, so the debug reloader running this twice is harmless.
with app.app_context():
    init_db()
    seed_db()

# Matches the "Min. 8 characters" placeholder on the registration form.
MIN_PASSWORD_LENGTH = 8


# ------------------------------------------------------------------ #
# Helpers                                                             #
# ------------------------------------------------------------------ #

def _validate_registration(name, email, password):
    """Return an error message, or None when the submission is usable.

    The form's `required` attributes are a browser convenience, not a
    guarantee about what reaches the route, so every field is checked again
    on the server.
    """
    if not name:
        return "Please enter your name."

    local, _, domain = email.partition("@")
    if email.count("@") != 1 or not local or not domain:
        return "Please enter a valid email address."

    if len(password) < MIN_PASSWORD_LENGTH:
        return f"Password must be at least {MIN_PASSWORD_LENGTH} characters."

    return None


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")

    name = request.form.get("name", "").strip()
    # Lowercased because SQLite's UNIQUE is case-sensitive: without this,
    # Demo@Spendly.com would become a second account beside demo@spendly.com.
    email = request.form.get("email", "").strip().lower()
    # Deliberately not stripped — spaces are legitimate password characters.
    password = request.form.get("password", "")

    error = _validate_registration(name, email, password)
    if error is None:
        try:
            create_user(name, email, password)
        except sqlite3.IntegrityError:
            # users.email is the table's only unique column, so an integrity
            # error here can only mean the address is already taken.
            error = "That email is already registered."

    if error:
        # 400 so a rejected submission is distinguishable from a fresh GET.
        return (
            render_template("register.html", error=error, name=name, email=email),
            400,
        )

    # No session and no flash() yet — those arrive with Step 3. The query
    # parameter carries the one message this step needs.
    return redirect(url_for("login", registered=1))


@app.route("/login")
def login():
    return render_template("login.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    return "Logout — coming in Step 3"


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
