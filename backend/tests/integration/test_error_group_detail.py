import shutil

from src.models.error_group import ErrorGroup
from src.scanning.log_scan_service import run_log_scan
from src.scanning.scan_service import run_scan


def test_stack_trace_group_exposes_complete_example_and_timestamps(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    run_log_scan(db_session, str(fixtures_dir / "logs"))

    group = next(
        g
        for g in db_session.query(ErrorGroup).all()
        if "Unhandled exception" in g.normalized_template
    )

    # Acceptance Scenario 1: complete original text, including continuation lines.
    assert "at handleRequest" in group.example_text
    assert "Caused by:" in group.example_text
    assert "at parseBody" in group.example_text

    assert len(group.occurrences) == 1
    occurrence = group.occurrences[0]
    assert occurrence.occurred_at is not None
    assert group.first_seen == occurrence.occurred_at
    assert group.last_seen == occurrence.occurred_at


def test_group_with_no_extractable_timestamp_still_has_example(tmp_path, db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    scratch = tmp_path / "logs"
    shutil.copytree(fixtures_dir / "logs" / "payments-api", scratch / "payments-api")
    # No timestamp prefix at all -- extract_timestamp must return None for it.
    (scratch / "payments-api" / "no-timestamp.log").write_text(
        "ERROR something broke, no timestamp prefix on this line\n", encoding="utf-8"
    )

    run_log_scan(db_session, str(scratch))

    group = next(
        g
        for g in db_session.query(ErrorGroup).all()
        if "no timestamp prefix" in g.normalized_template
    )

    # Acceptance Scenario 2: still shown, without a fabricated timestamp.
    assert group.first_seen is None
    assert group.last_seen is None
    assert group.example_text
    assert group.occurrences[0].occurred_at is None
