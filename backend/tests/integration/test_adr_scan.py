import shutil
from datetime import date

from src.models.adr_import_issue import AdrImportIssue
from src.models.adr_record import AdrRecord
from src.scanning.scan_service import run_scan


def test_adr_scan_imports_valid_records_and_isolates_failures(db_session, fixtures_dir):
    summary = run_scan(db_session, [str(fixtures_dir / "adr-repo")])

    records = db_session.query(AdrRecord).all()
    assert len(records) == 4  # 0001, 0002, 0003, secret-leak
    assert summary.adrs_found == 4

    by_title = {r.title: r for r in records}
    assert by_title["First Decision"].normalized_status == "accepted"
    assert by_title["First Decision"].date == date(2026, 1, 1)
    assert by_title["Second Decision"].normalized_status == "superseded"
    assert by_title["Secret Leak Decision"].has_secret_warning is True
    assert by_title["First Decision"].has_secret_warning is False

    # FR-008: broken.md isolated as an issue, not a record.
    issues = db_session.query(AdrImportIssue).all()
    assert any("broken.md" in i.path for i in issues)

    # FR-002: a non-Markdown file in docs/adr/ is silently excluded --
    # neither a record nor an issue.
    assert not any(r.source_path.endswith("diagram.png") for r in records)
    assert not any(i.path.endswith("diagram.png") for i in issues)


def test_same_filename_in_different_repos_stays_distinct(db_session, fixtures_dir):
    run_scan(
        db_session,
        [str(fixtures_dir / "adr-repo"), str(fixtures_dir / "adr-repo-2")],
    )

    records = db_session.query(AdrRecord).filter(AdrRecord.title.like("%First Decision%")).all()

    # "First Decision" (adr-repo) and "A Completely Different First
    # Decision" (adr-repo-2) both come from a file literally named
    # 0001-first-decision.md -- they must remain two distinct records,
    # scoped by source_path (Edge Case).
    assert len(records) == 2
    assert len({r.source_path for r in records}) == 2


def test_rescan_reflects_added_and_removed_adr(tmp_path, db_session, fixtures_dir):
    scratch = tmp_path / "adr-repo"
    shutil.copytree(fixtures_dir / "adr-repo", scratch)

    run_scan(db_session, [str(scratch)])
    titles_before = {r.title for r in db_session.query(AdrRecord).all()}
    assert "First Decision" in titles_before

    (scratch / "docs" / "adr" / "0001-first-decision.md").unlink()
    (scratch / "docs" / "adr" / "0004-fourth-decision.md").write_text(
        "# Fourth Decision\n\n* Status: proposed\n* Date: 2026-01-06\n",
        encoding="utf-8",
    )

    run_scan(db_session, [str(scratch)])
    titles_after = {r.title for r in db_session.query(AdrRecord).all()}

    # FR-012/SC-006: re-scan replaces the imported set to match current state.
    assert "First Decision" not in titles_after
    assert "Fourth Decision" in titles_after
