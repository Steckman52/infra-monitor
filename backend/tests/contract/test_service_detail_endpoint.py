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
    # Polish round: present even with none, as empty lists
    assert body["related_adrs"] == []
    assert body["recent_error_groups"] == []


def test_get_service_detail_404_for_unknown_id(client):
    response = client.get("/api/services/99999")

    assert response.status_code == 404


def test_get_service_detail_includes_related_adrs(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})
    services = {s["name"]: s for s in client.get("/api/services").json()}
    adrs = {a["title"]: a for a in client.get("/api/adrs").json()}

    response = client.get(f"/api/services/{services['adr-service-a']['id']}")

    assert response.status_code == 200
    related_titles = {a["title"] for a in response.json()["related_adrs"]}
    assert related_titles == set(adrs.keys())


def test_get_service_detail_includes_recent_error_groups(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "repo-node")]})
    client.post("/api/log-scan", json={"root": str(fixtures_dir / "logs")})
    services = client.get("/api/services").json()
    target = next(s for s in services if s["name"] == "payments-api")

    response = client.get(f"/api/services/{target['id']}")

    assert response.status_code == 200
    groups = response.json()["recent_error_groups"]
    assert len(groups) > 0
    assert all(g["service_id"] == target["id"] for g in groups)
