import pytest

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency
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


def test_non_object_json_raises_manifest_parse_error(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text("[1, 2, 3]", encoding="utf-8")

    with pytest.raises(ManifestParseError):
        package_json.parse(manifest)


def test_dependencies_not_an_object_raises_manifest_parse_error(tmp_path):
    # A real npm tool would never write this, but nothing stops a hand-edited
    # or generated package.json from doing so -- previously crashed the whole
    # scan with an uncaught AttributeError on list.items().
    manifest = tmp_path / "package.json"
    manifest.write_text('{"name": "x", "dependencies": ["not", "a", "dict"]}', encoding="utf-8")

    with pytest.raises(ManifestParseError):
        package_json.parse(manifest)


def test_non_string_dependency_version_is_treated_as_not_declared(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text(
        '{"name": "x", "dependencies": {"react": {"version": "18.0.0"}}}', encoding="utf-8"
    )

    result = package_json.parse(manifest)

    assert result.dependencies == [ParsedDependency(name="react", declared_version=None)]


def test_dev_and_optional_dependencies_are_included(tmp_path):
    # A frontend app whose every dependency is a devDependency previously
    # registered as having none at all.
    manifest = tmp_path / "package.json"
    manifest.write_text(
        """{
          "private": true,
          "devDependencies": {"vite": "^8.0.0", "tailwindcss": "^4.0.0"},
          "optionalDependencies": {"fsevents": "^2.3.0"}
        }""",
        encoding="utf-8",
    )

    result = package_json.parse(manifest)

    assert {d.name for d in result.dependencies} == {"vite", "tailwindcss", "fsevents"}


def test_peer_dependencies_are_not_treated_as_own_dependencies(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text(
        '{"name": "lib", "peerDependencies": {"react": "^19.0.0"}}', encoding="utf-8"
    )

    result = package_json.parse(manifest)

    assert result.dependencies == []


def test_package_listed_twice_keeps_the_runtime_version(tmp_path):
    manifest = tmp_path / "package.json"
    manifest.write_text(
        """{
          "name": "app",
          "dependencies": {"typescript": "^5.0.0"},
          "devDependencies": {"typescript": "^4.9.0"}
        }""",
        encoding="utf-8",
    )

    result = package_json.parse(manifest)

    assert result.dependencies == [ParsedDependency(name="typescript", declared_version="^5.0.0")]


def test_deeply_nested_json_raises_manifest_parse_error(tmp_path):
    # json.loads raises RecursionError (not JSONDecodeError) on pathologically
    # nested input -- previously uncaught, crashing the whole scan request.
    manifest = tmp_path / "package.json"
    depth = 5000
    manifest.write_text("[" * depth + "]" * depth, encoding="utf-8")

    with pytest.raises(ManifestParseError):
        package_json.parse(manifest)
