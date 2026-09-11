from src.models.service import Service
from src.scanning.scan_service import run_scan


def test_service_detail_matches_manifest_dependencies(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])

    service = db_session.query(Service).one()

    dep_pairs = {(d.name, d.declared_version) for d in service.dependencies}
    assert dep_pairs == {("express", "^4.18.0"), ("lodash", "^4.17.21")}


def test_service_with_no_dependencies_shows_empty_list(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-no-deps")])

    service = db_session.query(Service).one()

    assert service.dependencies == []
