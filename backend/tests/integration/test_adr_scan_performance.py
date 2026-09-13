import time

from src.models.adr_record import AdrRecord
from src.scanning.scan_service import run_scan

ADR_COUNT = 300


def test_scanning_a_few_hundred_adrs_completes_quickly(tmp_path, db_session):
    adr_dir = tmp_path / "big-repo" / "docs" / "adr"
    adr_dir.mkdir(parents=True)

    for i in range(ADR_COUNT):
        filename = f"{i:04d}-decision.md"
        content = f"# Decision {i}\n\n* Status: accepted\n* Date: 2026-01-01\n"
        if i > 0:
            # every ADR (after the first) supersedes the previous one, so
            # relationship resolution has real cross-file work to do, not
            # just a flat unlinked set.
            previous = f"{i - 1:04d}-decision.md"
            content += f"\n## Links\n\n* Supersedes [Decision {i - 1}]({previous})\n"
        (adr_dir / filename).write_text(content, encoding="utf-8")

    start = time.monotonic()
    summary = run_scan(db_session, [str(tmp_path / "big-repo")])
    elapsed = time.monotonic() - start

    assert summary.adrs_found == ADR_COUNT
    assert db_session.query(AdrRecord).count() == ADR_COUNT
    assert elapsed < 5.0
