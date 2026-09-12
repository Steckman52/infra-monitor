def test_get_log_scan_issues_lists_issues(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})

    response = client.get("/api/log-scan-issues")

    assert response.status_code == 200
    issues = response.json()
    assert len(issues) == 3  # 2 unattributed dirs + 1 unreadable file
    types = {issue["issue_type"] for issue in issues}
    assert types == {"unattributed", "unreadable"}


def test_get_log_scan_issues_before_any_scan_is_empty(client):
    response = client.get("/api/log-scan-issues")

    assert response.status_code == 200
    assert response.json() == []
