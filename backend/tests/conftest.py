from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

from src.db import Base, make_engine


@pytest.fixture()
def db_engine(tmp_path):
    engine = make_engine(tmp_path / "test.db")

    from src.models import dependency, scan_issue, service  # noqa: F401

    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture()
def db_session(db_engine):
    session_factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = session_factory()
    yield session
    session.close()


@pytest.fixture()
def client(db_engine):
    from fastapi.testclient import TestClient

    from src.db import get_session
    from src.main import app

    session_factory = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)

    def override_get_session():
        session = session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_session] = override_get_session
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def fixtures_dir() -> Path:
    return Path(__file__).parent / "integration" / "fixtures"
