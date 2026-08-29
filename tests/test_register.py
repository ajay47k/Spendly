"""Step 2 — registration.

The `app` fixture seeds the database, so every test starts with exactly one
user: the demo account. That row is what the duplicate-email cases collide
with, and the baseline every count assertion is measured against.
"""

from werkzeug.security import check_password_hash

import database.db as db

VALID = {
    "name": "Nitish Kumar",
    "email": "nitish@example.com",
    "password": "correct horse",
}


def users():
    conn = db.get_db()
    try:
        return conn.execute("SELECT * FROM users ORDER BY id").fetchall()
    finally:
        conn.close()


def test_get_register_renders(client):
    assert client.get("/register").status_code == 200


def test_valid_registration_creates_user(client):
    response = client.post("/register", data=VALID)

    # 405 until Step 2 wired up the POST branch.
    assert response.status_code == 302
    assert response.headers["Location"] == "/login?registered=1"

    rows = users()
    assert len(rows) == 2
    assert rows[-1]["email"] == VALID["email"]
    assert rows[-1]["name"] == VALID["name"]


def test_password_is_hashed(client):
    client.post("/register", data=VALID)

    stored = users()[-1]["password_hash"]
    assert stored != VALID["password"]
    assert check_password_hash(stored, VALID["password"])


def test_duplicate_email_rejected(client):
    response = client.post(
        "/register", data={**VALID, "email": db.DEMO_USER["email"]}
    )

    assert response.status_code == 400
    assert b"already registered" in response.data
    assert len(users()) == 1


def test_duplicate_email_is_case_and_space_insensitive(client):
    """Without .strip().lower() this would slip past a case-sensitive UNIQUE."""
    response = client.post(
        "/register", data={**VALID, "email": "  DEMO@Spendly.com  "}
    )

    assert response.status_code == 400
    assert len(users()) == 1


def test_short_password_rejected(client):
    response = client.post("/register", data={**VALID, "password": "1234567"})

    assert response.status_code == 400
    assert b"at least 8 characters" in response.data
    assert len(users()) == 1


def test_blank_name_rejected(client):
    """`required` is a browser convenience; the server has to check too."""
    response = client.post("/register", data={**VALID, "name": "   "})

    assert response.status_code == 400
    assert len(users()) == 1


def test_malformed_email_rejected(client):
    for bad in ("nitish.example.com", "@example.com", "nitish@", "a@b@c.com"):
        response = client.post("/register", data={**VALID, "email": bad})
        assert response.status_code == 400, bad
        assert len(users()) == 1, bad


def test_rejected_submission_keeps_fields(client):
    response = client.post(
        "/register",
        data={"name": "Nitish Kumar", "email": "nitish@example.com", "password": "x"},
    )

    body = response.data.decode()
    assert 'value="Nitish Kumar"' in body
    assert 'value="nitish@example.com"' in body
    # The password is never echoed back into the HTML.
    assert 'value="x"' not in body


def test_login_page_shows_success_banner(client):
    assert b"auth-success" in client.get("/login?registered=1").data
    assert b"auth-success" not in client.get("/login").data
