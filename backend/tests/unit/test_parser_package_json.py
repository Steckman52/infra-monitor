import pytest

from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import package_json


def test_parses_name_and_dependencies(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text(
        '{"name": "payments-api", "dependencies": {"express": "^4.18.0"}}',
        encoding="utf-8",
    )

    result = package_json.parse(manifest)

    assert result.name == "payments-api"
    assert result.is_complete is True
    assert [(d.name, d.declared_version) for d in result.dependencies] == [
        ("express", "^4.18.0")
    ]


def test_missing_name_field_returns_none(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text('{"dependencies": {}}', encoding="utf-8")

    result = package_json.parse(manifest)

    assert result.name is None
    assert result.dependencies == []


def test_invalid_json_raises_manifest_parse_error(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text('{"name": "broken"  "dependencies": {}}', encoding="utf-8")

    with pytest.raises(ManifestParseError):
        package_json.parse(manifest)
