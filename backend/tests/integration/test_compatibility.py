from src.analysis.version_compatibility import compute_compatibility
from src.scanning.scan_service import run_scan


def test_compatibility_across_shared_dependency(db_session, fixtures_dir):
    run_scan(
        db_session,
        [
            str(fixtures_dir / "repo-shared-dep-a"),
            str(fixtures_dir / "repo-shared-dep-b"),
            str(fixtures_dir / "repo-shared-dep-c"),
        ],
    )

    groups = compute_compatibility(db_session)

    assert len(groups) == 1
    group = groups[0]
    assert group.name == "moment"
    assert group.status == "compatibility_risk"  # major 2 vs major 1 (Acceptance Scenario 2)
    assert group.has_not_comparable is True  # "workspace:*" is not comparable (Scenario 3)
    majors = {e.major_version for e in group.entries}
    assert majors == {2, 1, None}


def test_dependency_used_by_one_service_is_excluded(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])  # express + lodash, used nowhere else

    groups = compute_compatibility(db_session)

    assert groups == []  # Acceptance Scenario 4 / FR-001


def test_same_major_across_services_is_compatible(db_session, fixtures_dir):
    run_scan(
        db_session,
        [str(fixtures_dir / "repo-shared-dep-a"), str(fixtures_dir / "repo-shared-dep-d")],
    )
    # Both declare "moment" at major version 2 -> compatible, no not-comparable entries.

    groups = compute_compatibility(db_session)

    assert len(groups) == 1
    group = groups[0]
    assert group.status == "compatible"  # Acceptance Scenario 1
    assert group.has_not_comparable is False
    assert {e.major_version for e in group.entries} == {2}
