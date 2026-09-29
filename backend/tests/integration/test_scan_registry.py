from src.models.service import Service
from src.scanning.scan_service import run_scan

# Explicit list, not "the whole fixtures dir": other features (e.g.
# 002-dependency-map) add their own fixture repos to this same shared
# fixtures directory, and this test's expected counts must stay decoupled
# from that.
FEATURE_1_FIXTURE_DIRS = [
    "repo-node",
    "repo-java",
    "repo-python",
    "repo-go",
    "repo-php",
    "repo-no-deps",
    "repo-incomplete-java",
    "repo-monorepo",
    "repo-with-vendor",
    "repo-collision-a",
    "repo-collision-b",
    "repo-broken",
]


def test_full_scan_produces_expected_registry(db_session, fixtures_dir):
    roots = [str(fixtures_dir / name) for name in FEATURE_1_FIXTURE_DIRS]
    missing_root = str(fixtures_dir / "does-not-exist")

    summary = run_scan(db_session, [*roots, missing_root])

    # 12 manifests produce a service: repo-node, repo-java, repo-python, repo-go,
    # repo-php, repo-no-deps, repo-incomplete-java (incomplete but still a
    # service, FR-009), repo-monorepo/frontend + repo-monorepo/backend,
    # repo-with-vendor (the node_modules decoy is excluded, FR-006),
    # repo-collision-a, repo-collision-b.
    # repo-broken/package.json is invalid and produces no service (FR-007/FR-008).
    assert summary.services_found == 12
    assert missing_root in summary.unreachable_roots  # Acceptance Scenario 4, FR-010

    services = db_session.query(Service).all()
    names = [s.name for s in services]
    assert len(names) == len(set(names))  # SC-006: no two services share a name

    monorepo_services = [s for s in services if "repo-monorepo" in s.repository_path]
    assert len(monorepo_services) == 2  # Acceptance Scenario 2 / FR-005

    vendor_related = [s for s in services if "node_modules" in s.manifest_path or "venv" in s.manifest_path]
    assert vendor_related == []  # FR-006

    incomplete = [s for s in services if not s.is_complete]
    assert len(incomplete) == 1  # the repo-incomplete-java pom.xml


def test_rescan_replaces_prior_results(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    first_pass = db_session.query(Service).all()
    assert len(first_pass) == 1

    run_scan(db_session, [str(fixtures_dir / "repo-go")])
    second_pass = db_session.query(Service).all()

    assert len(second_pass) == 1
    assert second_pass[0].ecosystem == "go"  # repo-node's service is gone (FR-014)


def test_scan_where_every_root_is_unreachable_keeps_the_existing_registry(db_session, fixtures_dir):
    # A mistyped path, an unmounted share, or a laptop off VPN must not
    # destroy the registry: the scan roots are not persisted anywhere, so
    # the user would have no way to rebuild what the wipe removed.
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    assert len(db_session.query(Service).all()) == 1

    summary = run_scan(db_session, [str(fixtures_dir / "does-not-exist")])

    assert summary.services_found == 0
    assert summary.unreachable_roots  # the failure is still reported
    assert len(db_session.query(Service).all()) == 1  # ...but nothing was destroyed


def test_scan_with_one_reachable_root_still_replaces_as_usual(db_session, fixtures_dir):
    # The guard above must not weaken normal replacement: a scan that
    # reached at least one root is a real result and does replace.
    run_scan(db_session, [str(fixtures_dir / "repo-node")])

    run_scan(db_session, [str(fixtures_dir / "repo-go"), str(fixtures_dir / "does-not-exist")])

    services = db_session.query(Service).all()
    assert len(services) == 1
    assert services[0].ecosystem == "go"
