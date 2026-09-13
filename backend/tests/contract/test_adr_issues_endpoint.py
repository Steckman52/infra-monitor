def test_get_adr_issues_returns_both_issue_types(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})

    response = client.get("/api/adr-issues")

    assert response.status_code == 200
    issues = response.json()
    assert any(i["type"] == "parse_failure" for i in issues)
    assert any(i["type"] == "secret_warning" for i in issues)
    assert all({"type", "path", "reason"} <= set(i.keys()) for i in issues)


def test_get_adr_issues_before_any_scan_is_empty(client):
    response = client.get("/api/adr-issues")

    assert response.status_code == 200
    assert response.json() == []
