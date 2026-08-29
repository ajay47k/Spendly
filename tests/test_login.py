"""Step 3 — login and logout.

The `app` fixture seeds the database, so every test starts signed out with
exactly one account: the demo user. `DEMO_USER` holds its plaintext password,
which is the only place a plaintext password legitimately exists.
"""

import database.db as db

CREDENTIALS = {
    "email": db.DEMO_USER["email"],
    "password": db.DEMO_USER["password"],
}


def signed_in_as(client):
    """Return the user_id in the session cookie, or None when signed out."""
    with client.session_transaction() as sess:
        return sess.get("user_id")


def test_get_login_renders(client):
    assert client.get("/login").status_code == 200


def test_valid_login_redirects_to_profile(client):
    response = client.post("/login", data=CREDENTIALS)

    # 405 until Step 3 wired up the POST branch.
    assert response.status_code == 302
    assert response.headers["Location"] == "/profile"
    assert signed_in_as(client) is not None


def test_login_is_case_and_space_insensitive(client):
    """The address is normalised the same way /register normalises it."""
    response = client.post(
        "/login", data={**CREDENTIALS, "email": "  DEMO@Spendly.com  "}
    )

    assert response.status_code == 302
    assert signed_in_as(client) is not None


def test_wrong_password_rejected(client):
    response = client.post("/login", data={**CREDENTIALS, "password": "wrong"})

    assert response.status_code == 401
    assert b"Incorrect email or password." in response.data
    assert signed_in_as(client) is None


def test_unknown_email_is_indistinguishable_from_wrong_password(client):
    """Different messages for the two failures would leak which emails exist."""
    unknown = client.post(
        "/login", data={"email": "nobody@nowhere.com", "password": "whatever"}
    )
    wrong = client.post("/login", data={**CREDENTIALS, "password": "wrong"})

    assert unknown.status_code == wrong.status_code == 401
    assert b"Incorrect email or password." in unknown.data
    assert signed_in_as(client) is None


def test_failed_login_keeps_email_but_not_password(client):
    response = client.post(
        "/login", data={"email": "nitish@example.com", "password": "wrong"}
    )

    body = response.data.decode()
    assert 'value="nitish@example.com"' in body
    # The password is never echoed back into the HTML.
    assert 'value="wrong"' not in body


def test_navbar_reflects_signed_in_state(client):
    assert b"Log out" not in client.get("/").data

    client.post("/login", data=CREDENTIALS)
    body = client.get("/").data

    assert b"Log out" in body
    assert db.DEMO_USER["name"].encode() in body
    assert b"Get started" not in body


def test_logout_clears_the_session(client):
    client.post("/login", data=CREDENTIALS)

    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert signed_in_as(client) is None


def test_logout_while_signed_out_is_harmless(client):
    response = client.get("/logout")

    assert response.status_code == 302
    assert response.headers["Location"] == "/"


def test_registered_user_can_sign_in(client):
    """Step 2 hashes and Step 3 checks — this is where they have to agree."""
    new_user = {
        "name": "Nitish Kumar",
        "email": "nitish@example.com",
        "password": "correct horse",
    }
    client.post("/register", data=new_user)

    response = client.post(
        "/login",
        data={"email": new_user["email"], "password": new_user["password"]},
    )

    assert response.status_code == 302
    assert signed_in_as(client) is not None
