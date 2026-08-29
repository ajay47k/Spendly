"""SQLite data layer for Spendly — Step 1, Database Setup.

Raw sqlite3 and raw SQL on purpose: no ORM, no migration tool. Every query
here is parameterized; never build SQL with string formatting.
"""

import sqlite3
from datetime import date
from pathlib import Path

from werkzeug.security import generate_password_hash

# Project root, resolved from this file so the path holds no matter which
# directory the app is launched from. .gitignore excludes exactly this name.
DB_PATH = Path(__file__).resolve().parent.parent / "expense_tracker.db"

# The fixed category list. Every expense must use one of these values.
CATEGORIES = [
    "Food",
    "Transport",
    "Bills",
    "Health",
    "Entertainment",
    "Shopping",
    "Other",
]

DEMO_USER = {
    "name": "Demo User",
    "email": "demo@spendly.com",
    "password": "demo123",
}

# (amount, category, day_of_month, description) — one row per category, with
# Food appearing twice to make eight. Days are spread across the month.
SAMPLE_EXPENSES = [
    (4500.00, "Bills", 2, "Electricity bill"),
    (1250.50, "Food", 4, "Weekly groceries"),
    (1800.00, "Transport", 6, "Monthly metro pass"),
    (2050.00, "Health", 9, "Pharmacy and checkup"),
    (799.00, "Entertainment", 13, "Movie tickets"),
    (2399.00, "Shopping", 17, "Running shoes"),
    (650.00, "Other", 21, "Birthday gift"),
    (1980.00, "Food", 25, "Dinner with family"),
]


def get_db():
    """Return a connection with dict-like rows and foreign keys enforced."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    # SQLite defaults foreign keys OFF, and the pragma is per-connection —
    # so it has to be set here, on every connection, not once at setup.
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    """Create both tables. Safe to call on every startup."""
    conn = get_db()
    try:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    id            INTEGER PRIMARY KEY AUTOINCREMENT,
                    name          TEXT NOT NULL,
                    email         TEXT NOT NULL UNIQUE,
                    password_hash TEXT NOT NULL,
                    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS expenses (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id     INTEGER NOT NULL,
                    amount      REAL NOT NULL,
                    category    TEXT NOT NULL,
                    date        TEXT NOT NULL,
                    description TEXT,
                    created_at  TEXT NOT NULL DEFAULT (datetime('now')),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
                """
            )
    finally:
        conn.close()


def seed_db():
    """Insert the demo user and sample expenses, once."""
    conn = get_db()
    try:
        if conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"]:
            return

        today = date.today()
        with conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (
                    DEMO_USER["name"],
                    DEMO_USER["email"],
                    generate_password_hash(DEMO_USER["password"]),
                ),
            )
            user_id = cursor.lastrowid
            conn.executemany(
                """
                INSERT INTO expenses (user_id, amount, category, date, description)
                VALUES (?, ?, ?, ?, ?)
                """,
                [
                    (
                        user_id,
                        amount,
                        category,
                        # Clamp to today so no sample expense lands in the future
                        # when the month is still young.
                        today.replace(day=min(day, today.day)).isoformat(),
                        description,
                    )
                    for amount, category, day, description in SAMPLE_EXPENSES
                ],
            )
    finally:
        conn.close()


def create_user(name, email, password):
    """Insert a user with a hashed password. Returns the new row id.

    Raises sqlite3.IntegrityError when the email is already registered. The
    UNIQUE constraint is the authority on that, so callers catch the error
    rather than checking first — a "does this email exist?" SELECT would race
    with a concurrent insert between the read and the write.
    """
    conn = get_db()
    try:
        with conn:
            cursor = conn.execute(
                "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                (name, email, generate_password_hash(password)),
            )
        return cursor.lastrowid
    finally:
        conn.close()


def get_user_by_email(email):
    """Return the user row for an address, or None when there is no such user.

    Does no password checking of its own. The caller compares the hash, so that
    a missing user and a wrong password can be answered identically.
    """
    conn = get_db()
    try:
        return conn.execute(
            "SELECT * FROM users WHERE email = ?", (email,)
        ).fetchone()
    finally:
        conn.close()
