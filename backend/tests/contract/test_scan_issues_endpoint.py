def test_get_scan_issues_lists_issues(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-broken")]})

    response = client.get("/api/scan-issues")

    assert response.status_code == 200
    issues = response.json()
    assert len(issues) == 1
    issue = issues[0]
    assert issue["issue_type"] == "unparsable"
    assert "reason" in issue
    assert issue["service_id"] is None


def test_get_scan_issues_before_any_scan_is_empty(client):
    response = client.get("/api/scan-issues")

    assert response.status_code == 200
    assert response.json() == []
