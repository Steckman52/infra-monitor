import pytest
from sqlalchemy import text

from src.db import init_db, make_engine


def test_init_db_creates_a_fresh_database(tmp_path):
    engine = make_engine(tmp_path / "fresh.db")

    init_db(engine)  # must not raise

    with engine.connect() as conn:
        tables = conn.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).scalars().all()
    assert "services" in tables


def test_init_db_is_idempotent(tmp_path):
    engine = make_engine(tmp_path / "again.db")
    init_db(engine)

    init_db(engine)  # re-running against an up-to-date file is fine


def test_init_db_refuses_a_database_missing_a_column(tmp_path):
    """Simulates upgrading the tool with an old registry.db in place.

    `create_all` would leave the stale table untouched and every read of the
    new column would fail later as an opaque 500 on every page. Failing at
    startup with an instruction is the difference between a two-second fix
    and an afternoon of debugging.
    """
    db_path = tmp_path / "stale.db"
    engine = make_engine(db_path)
    init_db(engine)

    with engine.begin() as conn:
        conn.execute(text("ALTER TABLE services DROP COLUMN ecosystem"))

    with pytest.raises(RuntimeError) as excinfo:
        init_db(engine)

    message = str(excinfo.value)
    assert "services.ecosystem" in message
    assert "delete that file" in message  # tells the user what to actually do
