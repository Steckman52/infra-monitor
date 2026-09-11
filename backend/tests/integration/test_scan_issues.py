import shutil

from src.models.scan_issue import ScanIssue
from src.models.service import Service
from src.scanning.scan_service import run_scan


def test_full_scan_issue_lifecycle(tmp_path, db_session, fixtures_dir):
    scratch = tmp_path / "scratch"
    shutil.copytree(fixtures_dir / "repo-broken", scratch / "repo-broken")
    shutil.copytree(fixtures_dir / "repo-incomplete-java", scratch / "repo-incomplete-java")

    run_scan(db_session, [str(scratch)])

    issues = db_session.query(ScanIssue).all()
    unparsable = [i for i in issues if i.issue_type == "unparsable"]
    incomplete = [i for i in issues if i.issue_type == "incomplete_data"]

    # Acceptance Scenario 1: invalid manifest -> issue with a reason, no service.
    assert len(unparsable) == 1
    assert unparsable[0].service_id is None
    assert unparsable[0].reason

    # Acceptance Scenario 2: incomplete manifest -> service marked incomplete,
    # linked issue.
    assert len(incomplete) == 1
    assert incomplete[0].service_id is not None
    incomplete_service = db_session.get(Service, incomplete[0].service_id)
    assert incomplete_service.is_complete is False

    # Acceptance Scenario 3 / SC-005: fixing the manifest and re-scanning
    # removes the resolved issue.
    (scratch / "repo-broken" / "package.json").write_text(
        '{"name": "fixed-service", "dependencies": {}}', encoding="utf-8"
    )
    run_scan(db_session, [str(scratch)])
    issues_after_fix = db_session.query(ScanIssue).all()
    assert not any(i.issue_type == "unparsable" for i in issues_after_fix)
    assert db_session.query(Service).filter_by(name="fixed-service").count() == 1

    # FR-014 add sub-case: a brand-new manifest appears as a new service.
    shutil.copytree(fixtures_dir / "repo-node", scratch / "repo-node")
    run_scan(db_session, [str(scratch)])
    assert db_session.query(Service).filter_by(name="payments-api").count() == 1

    # FR-014 remove sub-case: deleting a manifest makes its service disappear.
    shutil.rmtree(scratch / "repo-node")
    run_scan(db_session, [str(scratch)])
    assert db_session.query(Service).filter_by(name="payments-api").count() == 0
