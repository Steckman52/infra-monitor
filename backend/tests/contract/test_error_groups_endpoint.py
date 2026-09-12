def test_get_error_groups_lists_groups(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})

    response = client.get("/api/error-groups")

    assert response.status_code == 200
    groups = response.json()
    assert len(groups) > 0
    group = groups[0]
    assert {
        "id",
        "service_id",
        "service_name",
        "unattributed_source_path",
        "normalized_template",
        "severity_marker",
        "occurrence_count",
    } <= set(group.keys())


def test_get_error_groups_before_any_scan_is_empty(client):
    response = client.get("/api/error-groups")

    assert response.status_code == 200
    assert response.json() == []
