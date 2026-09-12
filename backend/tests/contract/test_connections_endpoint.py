def test_get_connections_lists_nodes_and_edges(client, fixtures_dir):
    client.post(
        "/api/scan",
        json={
            "roots": [
                str(fixtures_dir / "compose" / "valid"),
                str(fixtures_dir / "repo-node"),
                str(fixtures_dir / "repo-go"),
            ]
        },
    )

    response = client.get("/api/connections")

    assert response.status_code == 200
    nodes = response.json()
    assert len(nodes) > 0
    entry = nodes[0]
    assert "node" in entry and "connections" in entry
    assert {"type", "id", "name"} <= set(entry["node"].keys())
    assert entry["connections"][0]["relationship_basis"] in {
        "shared_network",
        "depends_on",
        "both",
    }


def test_get_connections_before_any_scan_is_empty(client):
    response = client.get("/api/connections")

    assert response.status_code == 200
    assert response.json() == []
