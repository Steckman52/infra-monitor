import time

from src.scanning.scan_service import run_scan


def test_scan_of_500_manifests_completes_quickly(tmp_path, db_session):
    for i in range(500):
        repo_dir = tmp_path / f"service-{i:04d}"
        repo_dir.mkdir()
        (repo_dir / "package.json").write_text(
            '{"name": "service-%04d", "dependencies": {"lodash": "^4.17.21"}}' % i,
            encoding="utf-8",
        )

    start = time.perf_counter()
    summary = run_scan(db_session, [str(tmp_path)])
    elapsed = time.perf_counter() - start

    assert summary.services_found == 500
    assert elapsed < 30.0, f"scan of 500 manifests took {elapsed:.2f}s, expected < 30s"
