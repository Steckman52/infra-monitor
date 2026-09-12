import shutil

from src.models.external_node import ExternalNode
from src.models.service_connection import ServiceConnection
from src.scanning.scan_service import run_scan


def _bases_by_pair(connections):
    bases = {}
    for c in connections:
        a = c.from_service.name if c.from_service else c.from_external_node.name
        b = c.to_service.name if c.to_service else c.to_external_node.name
        bases[frozenset((a, b))] = c.relationship_basis
    return bases


def test_connections_from_compose_fixture(db_session, fixtures_dir):
    summary = run_scan(
        db_session,
        [
            str(fixtures_dir / "compose"),
            str(fixtures_dir / "repo-node"),
            str(fixtures_dir / "repo-go"),
        ],
    )

    # the broken docker-compose.yml is isolated, not fatal (Acceptance Scenario 4, FR-013)
    assert summary.issues_found >= 1

    external_nodes = db_session.query(ExternalNode).all()
    assert {n.name for n in external_nodes} == {"db", "cache"}  # Acceptance Scenario 3

    bases = _bases_by_pair(db_session.query(ServiceConnection).all())
    assert bases[frozenset(("payments-api", "inventory-service"))] == "shared_network"  # AS1
    assert bases[frozenset(("payments-api", "db"))] == "both"  # shared network + depends_on
    assert bases[frozenset(("inventory-service", "db"))] == "shared_network"
    assert bases[frozenset(("payments-api", "cache"))] == "depends_on"  # AS2: no shared network


def test_rescan_removes_connection_after_topology_change(tmp_path, db_session, fixtures_dir):
    scratch = tmp_path / "scratch"
    shutil.copytree(fixtures_dir / "compose" / "valid", scratch / "compose" / "valid")
    shutil.copytree(fixtures_dir / "repo-node", scratch / "repo-node")
    shutil.copytree(fixtures_dir / "repo-go", scratch / "repo-go")

    run_scan(db_session, [str(scratch)])
    bases_before = _bases_by_pair(db_session.query(ServiceConnection).all())
    worker_db_pair = frozenset(("inventory-service", "db"))
    assert worker_db_pair in bases_before  # purely a shared-network connection

    compose_path = scratch / "compose" / "valid" / "docker-compose.yml"
    content = compose_path.read_text(encoding="utf-8")
    content = content.replace("    networks:\n      - backend-net\n", "")
    compose_path.write_text(content, encoding="utf-8")

    run_scan(db_session, [str(scratch)])
    bases_after = _bases_by_pair(db_session.query(ServiceConnection).all())

    # FR-015/SC-005: the connection graph is persisted, so it must be
    # rebuilt on re-scan -- unlike compatibility, which recomputes on read.
    assert worker_db_pair not in bases_after
