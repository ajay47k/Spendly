"""Step 1 — the data layer's runtime guarantees.

The schema declares a UNIQUE email and a foreign key, but neither is enforced
merely by being declared: SQLite leaves foreign keys off by default, and the
pragma is per-connection. These tests exercise the behavior, not the DDL.
"""

import sqlite3

import pytest

import database.db as db


def test_get_db_row_access_and_pragma(temp_db):
    conn = db.get_db()
    try:
        row = conn.execute("SELECT 1 AS answer").fetchone()
        assert row["answer"] == 1  # sqlite3.Row, not a bare tuple
        assert conn.execute("PRAGMA foreign_keys").fetchone()[0] == 1
    finally:
        conn.close()


def test_init_db_is_idempotent(temp_db):
    # temp_db already ran the first init_db(); these must not raise.
    db.init_db()
    db.init_db()

    conn = db.get_db()
    try:
        tables = {
            r["name"]
            for r in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        }
    finally:
        conn.close()

    assert {"users", "expenses"} <= tables


def test_seed_db_does_not_duplicate(temp_db):
    db.seed_db()
    db.seed_db()
    db.seed_db()

    conn = db.get_db()
    try:
        assert conn.execute("SELECT COUNT(*) AS n FROM users").fetchone()["n"] == 1
        rows = conn.execute("SELECT * FROM expenses").fetchall()
    finally:
        conn.close()

    assert len(rows) == len(db.SAMPLE_EXPENSES)
    assert {r["category"] for r in rows} == set(db.CATEGORIES)
    # Section 11: dates stored as YYYY-MM-DD, consistently.
    for r in rows:
        assert len(r["date"]) == 10
        assert r["date"][4] == "-" and r["date"][7] == "-"
        assert isinstance(r["amount"], float)


def test_duplicate_email_rejected(temp_db):
    db.seed_db()

    conn = db.get_db()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            with conn:
                conn.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    ("Impostor", db.DEMO_USER["email"], "irrelevant"),
                )
    finally:
        conn.close()


def test_invalid_user_id_rejected(temp_db):
    """Regression test for get_db() dropping PRAGMA foreign_keys = ON.

    Without the pragma this insert succeeds silently and the test fails.
    """
    conn = db.get_db()
    try:
        with pytest.raises(sqlite3.IntegrityError):
            with conn:
                conn.execute(
                    "INSERT INTO expenses (user_id, amount, category, date) "
                    "VALUES (?, ?, ?, ?)",
                    (9999, 100.0, "Food", "2026-08-01"),
                )
    finally:
        conn.close()
