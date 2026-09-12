def test_get_error_group_detail_returns_full_shape(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})

    groups = client.get("/api/error-groups").json()
    target = groups[0]

    response = client.get(f"/api/error-groups/{target['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == target["id"]
    assert isinstance(body["occurrences"], list)
    assert len(body["occurrences"]) > 0
    occurrence = body["occurrences"][0]
    assert {"raw_text", "occurred_at", "source_log_path", "line_number"} <= set(
        occurrence.keys()
    )
    assert "example_text" in body


def test_get_error_group_detail_404_for_unknown_id(client):
    response = client.get("/api/error-groups/99999")

    assert response.status_code == 404
