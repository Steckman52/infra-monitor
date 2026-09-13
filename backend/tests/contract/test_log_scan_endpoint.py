def test_post_log_scan_returns_summary_shape(client, fixtures_dir):
    # "payments-api" (the log fixture's matching directory name) must
    # already exist in the registry for attribution to succeed.
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})

    response = client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["error_groups_found"], int)
    assert isinstance(body["issues_found"], int)
    assert body["root_unreachable"] is False


def test_post_log_scan_reports_unreachable_root(client, fixtures_dir):
    response = client.post("/api/log-scan", json={"root": str(fixtures_dir / "does-not-exist")})

    assert response.status_code == 200
    body = response.json()
    assert body["error_groups_found"] == 0
    assert body["root_unreachable"] is True


def test_post_log_scan_returns_503_when_database_is_locked(client, monkeypatch):
    def _raise_locked(*args, **kwargs):
        from sqlalchemy.exc import OperationalError

        raise OperationalError("statement", {}, Exception("database is locked"))

    monkeypatch.setattr("src.api.log_scan.run_log_scan", _raise_locked)

    response = client.post("/api/log-scan", json={"root": "irrelevant"})

    assert response.status_code == 503
    assert "already in progress" in response.json()["detail"]
