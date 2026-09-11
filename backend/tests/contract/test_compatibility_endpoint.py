def test_get_compatibility_lists_shared_dependencies(client, fixtures_dir):
    client.post(
        "/api/scan",
        json={
            "roots": [
                str(fixtures_dir / "repo-shared-dep-a"),
                str(fixtures_dir / "repo-shared-dep-b"),
                str(fixtures_dir / "repo-shared-dep-c"),
            ]
        },
    )

    response = client.get("/api/dependency-compatibility")

    assert response.status_code == 200
    groups = response.json()
    assert len(groups) == 1
    group = groups[0]
    assert group["name"] == "moment"
    assert group["ecosystem"] == "node"
    assert group["status"] == "compatibility_risk"
    assert group["has_not_comparable"] is True
    assert len(group["entries"]) == 3


def test_get_compatibility_before_any_scan_is_empty(client):
    response = client.get("/api/dependency-compatibility")

    assert response.status_code == 200
    assert response.json() == []
