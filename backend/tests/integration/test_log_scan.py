import shutil

from src.models.error_group import ErrorGroup
from src.models.log_scan_issue import LogScanIssue
from src.scanning.log_scan_service import run_log_scan
from src.scanning.scan_service import run_scan


def test_log_scan_groups_near_duplicates_and_captures_stack_trace(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])  # registers "payments-api"

    summary = run_log_scan(db_session, str(fixtures_dir / "logs"))

    groups = db_session.query(ErrorGroup).all()

    conn_refused = next(g for g in groups if "Connection refused" in g.normalized_template)
    assert conn_refused.occurrence_count == 12  # SC-001
    assert conn_refused.service.name == "payments-api"

    stack_trace_group = next(g for g in groups if "Unhandled exception" in g.normalized_template)
    assert "at handleRequest" in stack_trace_group.example_text
    assert "Caused by:" in stack_trace_group.example_text

    assert not any("Service started" in g.normalized_template for g in groups)

    # Edge Case: two unattributed dirs with identical text stay separate.
    unattributed_groups = [g for g in groups if g.service_id is None]
    assert len(unattributed_groups) == 2
    assert {g.unattributed_source_path for g in unattributed_groups} == {
        str(fixtures_dir / "logs" / "unknown-service"),
        str(fixtures_dir / "logs" / "another-unknown-service"),
    }

    assert summary.error_groups_found == len(groups)


def test_rescan_adds_new_group_without_duplicating_existing(tmp_path, db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    scratch = tmp_path / "logs"
    shutil.copytree(fixtures_dir / "logs" / "payments-api", scratch / "payments-api")

    run_log_scan(db_session, str(scratch))
    conn_refused_before = next(
        g
        for g in db_session.query(ErrorGroup).all()
        if "Connection refused" in g.normalized_template
    )
    assert conn_refused_before.occurrence_count == 12

    log_file = scratch / "payments-api" / "app.log"
    log_file.write_text(
        log_file.read_text(encoding="utf-8") + "2026-09-11 10:00:00 ERROR Totally new failure mode\n",
        encoding="utf-8",
    )

    run_log_scan(db_session, str(scratch))
    second_pass = db_session.query(ErrorGroup).all()

    assert any("Totally new failure mode" in g.normalized_template for g in second_pass)
    conn_refused_after = next(g for g in second_pass if "Connection refused" in g.normalized_template)
    assert conn_refused_after.occurrence_count == 12  # not duplicated (FR-015/SC-005)


def test_email_addresses_are_redacted_before_storage(tmp_path, db_session):
    log_dir = tmp_path / "logs" / "some-service"
    log_dir.mkdir(parents=True)
    (log_dir / "app.log").write_text(
        "2026-09-01 03:15:00 ERROR Login failed for john.doe@example.com\n",
        encoding="utf-8",
    )

    run_log_scan(db_session, str(tmp_path / "logs"))

    group = db_session.query(ErrorGroup).one()
    assert "john.doe@example.com" not in group.normalized_template
    assert "john.doe@example.com" not in group.example_text
    assert "[REDACTED_EMAIL]" in group.example_text
    occurrence = group.occurrences[0]
    assert "john.doe@example.com" not in occurrence.raw_text
    assert "[REDACTED_EMAIL]" in occurrence.raw_text


def test_nonexistent_root_reports_unreachable_instead_of_silent_zero(db_session, fixtures_dir):
    missing_root = str(fixtures_dir / "does-not-exist")

    summary = run_log_scan(db_session, missing_root)

    assert summary.error_groups_found == 0
    assert summary.root_unreachable is True

    issues = db_session.query(LogScanIssue).all()
    assert any(i.issue_type == "unreachable_path" and i.path == missing_root for i in issues)
