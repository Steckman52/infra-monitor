def test_pick_directory_returns_selected_path(client, monkeypatch):
    monkeypatch.setattr("src.api.filesystem.filedialog.askdirectory", lambda: "C:\\Users\\roma-\\repo")

    response = client.get("/api/pick-directory")

    assert response.status_code == 200
    assert response.json() == {"path": "C:\\Users\\roma-\\repo"}


def test_pick_directory_returns_null_when_cancelled(client, monkeypatch):
    monkeypatch.setattr("src.api.filesystem.filedialog.askdirectory", lambda: "")

    response = client.get("/api/pick-directory")

    assert response.status_code == 200
    assert response.json() == {"path": None}
