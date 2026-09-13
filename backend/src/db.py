from pathlib import Path

from sqlalchemy import create_engine, event
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "registry.db"


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


def init_db(bind_engine=engine) -> None:
    import src.models  # noqa: F401  (registers every model on Base)

    Base.metadata.create_all(bind=bind_engine)


def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
