def test_get_services_lists_registered_services(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir)]})

    response = client.get("/api/services")

    assert response.status_code == 200
    services = response.json()
    assert isinstance(services, list)
    assert len(services) > 0
    first = services[0]
    assert {"id", "name", "ecosystem", "repository_path", "is_complete"} <= set(
        first.keys()
    )


def test_get_services_before_any_scan_is_empty(client):
    response = client.get("/api/services")

    assert response.status_code == 200
    assert response.json() == []
