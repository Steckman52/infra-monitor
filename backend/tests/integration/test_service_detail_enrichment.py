def test_service_detail_shows_own_risk_and_connections(client, fixtures_dir):
    client.post(
        "/api/scan",
        json={
            "roots": [
                str(fixtures_dir / "repo-enriched-a"),
                str(fixtures_dir / "repo-enriched-b"),
                str(fixtures_dir / "compose" / "enriched"),
            ]
        },
    )

    services = client.get("/api/services").json()
    enriched_a = next(s for s in services if s["name"] == "enriched-service-a")

    detail = client.get(f"/api/services/{enriched_a['id']}").json()

    # Acceptance Scenario 1: this service's own compatibility risk is visible here.
    assert len(detail["compatibility_risks"]) == 1
    risk = detail["compatibility_risks"][0]
    assert risk["name"] == "winston"
    assert risk["declared_version"] == "^3.11.0"
    assert risk["conflicting_with"][0]["service_name"] == "enriched-service-b"

    # Acceptance Scenario 2: its docker-compose connection is visible here too.
    assert len(detail["connections"]) == 1
    connection = detail["connections"][0]
    assert connection["node"]["type"] == "external"
    assert connection["node"]["name"] == "cache"
    assert connection["relationship_basis"] == "depends_on"
