from pathlib import Path

import pytest
from sqlalchemy.orm import sessionmaker

from src.db import Base, make_engine


@pytest.fixture()
def db_engine(tmp_path):
    engine = make_engine(tmp_path / "test.db")

    import src.models  # noqa: F401  (registers every model on Base)

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
    # base_url matters: TrustedHostMiddleware rejects anything but
    # localhost/127.0.0.1, and TestClient's default Host is "testserver".
    # Using a real allowed host keeps that middleware on the tested path
    # rather than configuring it away for tests.
    with TestClient(app, base_url="http://localhost") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture()
def fixtures_dir() -> Path:
    return Path(__file__).parent / "integration" / "fixtures"
