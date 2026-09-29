import pytest

from src.api import log_scan, scan


def test_a_second_registry_scan_is_refused_while_one_is_running(client, fixtures_dir):
    # Two overlapping scans used to both complete and replace each other's
    # results, so the last one to commit silently won. Simulate the first
    # scan still being in progress by holding its lock.
    assert scan._scan_lock.acquire(blocking=False)
    try:
        response = client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    finally:
        scan._scan_lock.release()

    assert response.status_code == 409
    assert "already running" in response.json()["detail"]


def test_the_lock_is_released_after_a_scan_so_the_next_one_runs(client, fixtures_dir):
    roots = {"roots": [str(fixtures_dir / "repo-node")]}

    assert client.post("/api/scan", json=roots).status_code == 200
    assert client.post("/api/scan", json=roots).status_code == 200


def test_the_lock_is_released_even_when_a_scan_fails(client, monkeypatch):
    def _boom(*_args, **_kwargs):
        raise RuntimeError("scan blew up")

    monkeypatch.setattr(scan, "run_scan", _boom)
    # TestClient re-raises server-side exceptions into the test by default.
    with pytest.raises(RuntimeError):
        client.post("/api/scan", json={"roots": ["C:/anything"]})

    assert scan._scan_lock.acquire(blocking=False)  # not stuck held forever
    scan._scan_lock.release()


def test_a_second_log_scan_is_refused_while_one_is_running(client, fixtures_dir):
    assert log_scan._scan_lock.acquire(blocking=False)
    try:
        response = client.post("/api/log-scan", json={"root": str(fixtures_dir)})
    finally:
        log_scan._scan_lock.release()

    assert response.status_code == 409
