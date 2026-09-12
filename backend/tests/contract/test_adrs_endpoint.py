def test_get_adrs_lists_imported_adrs(client, fixtures_dir):
    client.post("/api/scan", json={"roots": [str(fixtures_dir / "adr-repo")]})

    response = client.get("/api/adrs")

    assert response.status_code == 200
    adrs = response.json()
    assert len(adrs) == 4  # 0001, 0002, 0003, secret-leak -- broken.md/diagram.png excluded
    entry = adrs[0]
    assert {"id", "title", "normalized_status", "raw_status", "date", "source_path", "has_secret_warning"} <= set(
        entry.keys()
    )


def test_get_adrs_before_any_scan_is_empty(client):
    response = client.get("/api/adrs")

    assert response.status_code == 200
    assert response.json() == []
