def test_get_dashboard_before_any_scan_is_all_zero(client):
    response = client.get("/api/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["services_count"] == 0
    assert body["scan_issues_count"] == 0
    assert body["compatibility_risks_count"] == 0
    assert body["error_groups_count"] == 0
    assert body["log_scan_issues_count"] == 0
    assert body["adrs_count"] == 0
    assert body["adr_issues_count"] == 0
    assert body["last_registry_scan_at"] is None
    assert body["last_log_scan_at"] is None


def test_get_dashboard_reflects_registry_and_adr_scan(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})

    response = client.get("/api/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["services_count"] == 2  # adr-service-a, adr-service-b
    assert body["adrs_count"] == 4  # 0001, 0002, 0003, secret-leak
    assert body["adr_issues_count"] == 2  # broken.md parse failure + secret-leak warning
    assert body["last_registry_scan_at"] is not None
    assert body["last_log_scan_at"] is None


def test_get_dashboard_reflects_log_scan_independently(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})

    response = client.get("/api/dashboard")

    assert response.status_code == 200
    body = response.json()
    assert body["error_groups_count"] > 0
    assert body["log_scan_issues_count"] > 0
    assert body["last_registry_scan_at"] is not None
    assert body["last_log_scan_at"] is not None
