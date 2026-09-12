import shutil

from src.models.error_group import ErrorGroup
from src.models.log_scan_issue import LogScanIssue
from src.scanning.log_scan_service import run_log_scan
from src.scanning.scan_service import run_scan


def test_unattributed_and_unreadable_issues_recorded(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])

    run_log_scan(db_session, str(fixtures_dir / "logs"))

    issues = db_session.query(LogScanIssue).all()

    unattributed = [i for i in issues if i.issue_type == "unattributed"]
    assert len(unattributed) == 2  # Acceptance Scenario 1
    assert {i.path for i in unattributed} == {
        str(fixtures_dir / "logs" / "unknown-service"),
        str(fixtures_dir / "logs" / "another-unknown-service"),
    }

    unreadable = [i for i in issues if i.issue_type == "unreadable"]
    assert len(unreadable) == 1  # Acceptance Scenario 2
    assert "broken-encoding.log" in unreadable[0].path
    assert unreadable[0].reason

    # FR-002: the .gz file produces no issue anywhere.
    assert not any(".gz" in i.path for i in issues)


def test_rescan_resolves_unattributed_issue_after_rename(tmp_path, db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    scratch = tmp_path / "logs"
    shutil.copytree(fixtures_dir / "logs" / "unknown-service", scratch / "unknown-service")

    run_log_scan(db_session, str(scratch))
    issues_before = db_session.query(LogScanIssue).all()
    assert len(issues_before) == 1
    assert issues_before[0].issue_type == "unattributed"

    (scratch / "unknown-service").rename(scratch / "payments-api")

    run_log_scan(db_session, str(scratch))
    issues_after = db_session.query(LogScanIssue).all()
    groups_after = db_session.query(ErrorGroup).all()

    # Acceptance Scenario 3 / FR-015/SC-005: resolved issue disappears, and
    # its errors now appear as a normal (attributed) group.
    assert issues_after == []
    assert len(groups_after) == 1
    assert groups_after[0].service.name == "payments-api"
