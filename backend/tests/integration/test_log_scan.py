import shutil

from src.models.error_group import ErrorGroup
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
