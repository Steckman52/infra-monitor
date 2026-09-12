def test_post_log_scan_returns_summary_shape(client, fixtures_dir):
    # "payments-api" (the log fixture's matching directory name) must
    # already exist in the registry for attribution to succeed.
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})

    response = client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["error_groups_found"], int)
    assert isinstance(body["issues_found"], int)
