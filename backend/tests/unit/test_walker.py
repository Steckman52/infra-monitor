from src.scanning import walker


def test_find_manifests_stops_after_the_directory_cap(tmp_path, monkeypatch):
    monkeypatch.setattr(walker, "MAX_DIRECTORIES_WALKED", 3)
    for i in range(10):
        sub = tmp_path / f"repo-{i}"
        sub.mkdir()
        (sub / "package.json").write_text('{"name": "x"}', encoding="utf-8")

    found = list(walker.find_manifests(tmp_path))

    # The root directory itself plus at most 3 subdirectories are visited --
    # never all 10 -- so far fewer than 10 manifests are found.
    assert 0 < len(found) < 10


def test_find_manifests_finds_everything_under_the_cap(tmp_path):
    for i in range(3):
        sub = tmp_path / f"repo-{i}"
        sub.mkdir()
        (sub / "package.json").write_text('{"name": "x"}', encoding="utf-8")

    found = list(walker.find_manifests(tmp_path))

    assert len(found) == 3
