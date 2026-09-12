def test_get_service_detail_returns_full_shape(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    services = client.get("/api/services").json()
    target = services[0]

    response = client.get(f"/api/services/{target['id']}")

    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "payments-api"
    assert isinstance(body["dependencies"], list)
    assert {"manifest_path", "last_scanned_at", "ecosystem", "repository_path"} <= set(
        body.keys()
    )
    # 002 US3: present even for a service with neither, as empty lists
    assert body["compatibility_risks"] == []
    assert body["connections"] == []


def test_get_service_detail_404_for_unknown_id(client):
    response = client.get("/api/services/99999")

    assert response.status_code == 404
