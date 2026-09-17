import pytest

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency
from src.scanning.parsers import composer_json


def test_parses_name_and_require(tmp_path):
    manifest = tmp_path / "composer.json"
    manifest.write_text(
        '{"name": "example/billing-service", '
        '"require": {"php": ">=8.1", "monolog/monolog": "^3.0"}}',
        encoding="utf-8",
    )

    result = composer_json.parse(manifest)

    assert result.name == "example/billing-service"
    names = [d.name for d in result.dependencies]
    assert "monolog/monolog" in names
    assert "php" not in names  # runtime version constraint, not a real dependency


def test_non_object_json_raises_manifest_parse_error(tmp_path):
    manifest = tmp_path / "composer.json"
    manifest.write_text("42", encoding="utf-8")

    with pytest.raises(ManifestParseError):
        composer_json.parse(manifest)


def test_require_not_an_object_raises_manifest_parse_error(tmp_path):
    manifest = tmp_path / "composer.json"
    manifest.write_text('{"name": "x", "require": ["not", "a", "dict"]}', encoding="utf-8")

    with pytest.raises(ManifestParseError):
        composer_json.parse(manifest)


def test_non_string_require_version_is_treated_as_not_declared(tmp_path):
    manifest = tmp_path / "composer.json"
    manifest.write_text(
        '{"name": "x", "require": {"monolog/monolog": {"version": "3.0"}}}', encoding="utf-8"
    )

    result = composer_json.parse(manifest)

    assert result.dependencies == [ParsedDependency(name="monolog/monolog", declared_version=None)]


def test_deeply_nested_json_raises_manifest_parse_error(tmp_path):
    manifest = tmp_path / "composer.json"
    depth = 5000
    manifest.write_text("[" * depth + "]" * depth, encoding="utf-8")

    with pytest.raises(ManifestParseError):
        composer_json.parse(manifest)
