import pytest

from src.scanning import walker


def test_find_manifests_announces_the_directory_cap(tmp_path, monkeypatch):
    # Truncation must be loud. Silently returning a subset told the operator
    # a service did not exist when the walker had merely stopped early.
    monkeypatch.setattr(walker, "MAX_DIRECTORIES_WALKED", 3)
    for i in range(10):
        sub = tmp_path / f"repo-{i}"
        sub.mkdir()
        (sub / "package.json").write_text('{"name": "x"}', encoding="utf-8")

    with pytest.raises(walker.WalkTruncated):
        list(walker.find_manifests(tmp_path))


def test_find_manifests_finds_everything_under_the_cap(tmp_path):
    for i in range(3):
        sub = tmp_path / f"repo-{i}"
        sub.mkdir()
        (sub / "package.json").write_text('{"name": "x"}', encoding="utf-8")

    found = list(walker.find_manifests(tmp_path))

    assert len(found) == 3


@pytest.mark.parametrize(
    "filename, expected",
    [
        ("app.log", True),
        ("notes.txt", True),
        ("app.log.1", True),  # rotated logs are the history, not noise
        ("app.log.2026-01-01", True),
        ("app.log.2.gz", False),  # not readable as text
        # Extensionless files are not logs. Admitting them meant reading
        # private keys and credential stores in full.
        (".env", False),
        ("id_rsa", False),
        ("credentials", False),
        (".npmrc", False),
        (".bash_history", False),
        (".pgpass", False),
    ],
)
def test_only_readable_log_shaped_files_are_scanned(filename, expected):
    assert walker.is_log_file(filename) is expected


def test_credential_directories_are_pruned():
    for name in (".ssh", ".aws", ".gnupg"):
        assert name in walker.EXCLUDED_DIR_NAMES
