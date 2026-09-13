def test_get_adr_detail_returns_relationships_and_services(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})
    adrs = {a["title"]: a for a in client.get("/api/adrs").json()}
    second_id = adrs["Second Decision"]["id"]
    third_id = adrs["Third Decision"]["id"]

    response = client.get(f"/api/adrs/{third_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["title"] == "Third Decision"
    assert "content" in body
    assert {"supersedes", "superseded_by", "amends", "amended_by", "related_services"} <= set(
        body.keys()
    )
    assert body["supersedes"] == [{"adr_id": second_id, "title": "Second Decision"}]
    assert body["superseded_by"] == []
    assert body["amends"] == []
    assert body["amended_by"] == []
    service_names = {s["service_name"] for s in body["related_services"]}
    assert service_names == {"adr-service-a", "adr-service-b"}


def test_second_decision_shows_superseded_by(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})
    adrs = {a["title"]: a for a in client.get("/api/adrs").json()}
    second_id = adrs["Second Decision"]["id"]
    third_id = adrs["Third Decision"]["id"]

    response = client.get(f"/api/adrs/{second_id}")

    assert response.status_code == 200
    body = response.json()
    assert body["superseded_by"] == [{"adr_id": third_id, "title": "Third Decision"}]


def test_get_adr_detail_404_when_missing(client):
    response = client.get("/api/adrs/999")

    assert response.status_code == 404
