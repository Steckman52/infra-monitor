import time

from src.scanning.log_scan_service import run_log_scan
from src.scanning.scan_service import run_scan


def test_log_scan_of_10000_lines_completes_quickly(tmp_path, db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])  # registers "payments-api"

    log_dir = tmp_path / "logs" / "payments-api"
    log_dir.mkdir(parents=True)
    lines = []
    for i in range(10_000):
        if i % 50 == 0:
            lines.append(f"2026-09-01 00:00:00 ERROR Connection refused: db:5432 attempt {i}")
        else:
            lines.append(f"2026-09-01 00:00:00 INFO Processed request {i}")
    (log_dir / "app.log").write_text("\n".join(lines) + "\n", encoding="utf-8")

    start = time.perf_counter()
    summary = run_log_scan(db_session, str(tmp_path / "logs"))
    elapsed = time.perf_counter() - start

    assert summary.error_groups_found >= 1
    assert elapsed < 10.0, f"log scan of 10,000 lines took {elapsed:.2f}s, expected well under 10s"
