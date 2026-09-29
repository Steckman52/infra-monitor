from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from src.config import DB_PATH as DEFAULT_DB_PATH


class Base(DeclarativeBase):
    pass


def make_engine(db_path: Path = DEFAULT_DB_PATH):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        # Give a second, overlapping scan a real window to finish instead of
        # failing immediately on SQLite's default ~5s wait when this
        # connection's writer lock is briefly held by another one.
        cursor.execute("PRAGMA busy_timeout=15000")
        cursor.close()

    return engine


engine = make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def _missing_columns(bind_engine) -> list[str]:
    """Columns the models declare that the database on disk lacks.

    `create_all` creates missing *tables* and never alters existing ones, so
    a database written by an older version keeps its old shape and every
    read touching a new column fails with "no such column" -- as an opaque
    500, on every page. Every row here is derived from files on disk, so
    rebuilding is free; the only unacceptable outcome is the silent one.
    """
    from sqlalchemy import inspect

    inspector = inspect(bind_engine)
    existing_tables = set(inspector.get_table_names())
    missing: list[str] = []
    for table_name, table in Base.metadata.tables.items():
        if table_name not in existing_tables:
            continue  # create_all will make it
        on_disk = {col["name"] for col in inspector.get_columns(table_name)}
        missing.extend(
            f"{table_name}.{column.name}" for column in table.columns if column.name not in on_disk
        )
    return missing


def init_db(bind_engine=engine) -> None:
    import src.models  # noqa: F401  (registers every model on Base)

    outdated = _missing_columns(bind_engine)
    if outdated:
        db_file = bind_engine.url.database
        raise RuntimeError(
            f"The database at {db_file} was created by an older version and is missing: "
            f"{', '.join(outdated)}. Everything in it is rebuilt from disk by a scan, so "
            f"delete that file and start again to pick up the new schema."
        )

    Base.metadata.create_all(bind=bind_engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
