"""Shared pytest fixtures.

pytest-flask's `client` fixture only works when an `app` fixture hands it the
Flask instance, so that lives here for Steps 2-9 to use.
"""

import pytest

import database.db as db


@pytest.fixture
def temp_db(tmp_path, monkeypatch):
    """Point the data layer at a throwaway database and create the schema.

    Patching the module global is enough because get_db() looks up DB_PATH at
    call time rather than capturing it at import.
    """
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()
    return db.DB_PATH


@pytest.fixture
def app(temp_db):
    """The Flask app, wired to the temp database.

    Imported inside the fixture, not at module scope: app.py calls init_db()
    and seed_db() at import time, so importing it before temp_db has patched
    DB_PATH would create and seed the real expense_tracker.db in the project
    root as a side effect of running the tests. Seeding again here because
    sys.modules caches the module, so the import-time seed runs only once.
    """
    import app as app_module

    db.seed_db()
    app_module.app.config.update(TESTING=True)
    return app_module.app
