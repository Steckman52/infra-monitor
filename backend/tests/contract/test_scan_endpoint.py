def test_post_scan_returns_summary_shape(client, fixtures_dir):
    response = client.post("/api/scan", json={"roots": [str(fixtures_dir)]})

    assert response.status_code == 200
    body = response.json()
    assert isinstance(body["services_found"], int)
    assert isinstance(body["issues_found"], int)
    assert isinstance(body["unreachable_roots"], list)
    assert isinstance(body["adrs_found"], int)


def test_post_scan_reports_unreachable_root(client, fixtures_dir):
    missing_root = str(fixtures_dir / "does-not-exist")

    response = client.post("/api/scan", json={"roots": [missing_root]})

    assert response.status_code == 200
    body = response.json()
    assert missing_root in body["unreachable_roots"]
