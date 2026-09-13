import pytest

from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import go_mod


def test_parses_module_name_and_requires(tmp_path):
    manifest = tmp_path / "go.mod"
    manifest.write_text(
        "module github.com/example/inventory-service\n\n"
        "go 1.21\n\n"
        "require (\n\tgithub.com/gin-gonic/gin v1.9.1\n)\n",
        encoding="utf-8",
    )

    result = go_mod.parse(manifest)

    assert result.name == "inventory-service"  # last path segment of module directive
    assert result.dependencies[0].name == "github.com/gin-gonic/gin"
    assert result.dependencies[0].declared_version == "v1.9.1"


def test_missing_module_directive_raises(tmp_path):
    manifest = tmp_path / "go.mod"
    manifest.write_text("go 1.21\n", encoding="utf-8")

    with pytest.raises(ManifestParseError):
        go_mod.parse(manifest)


def test_non_utf8_bytes_raise_manifest_parse_error(tmp_path):
    manifest = tmp_path / "go.mod"
    manifest.write_bytes(b"module x\n\xff\xfe invalid utf-8 bytes")

    with pytest.raises(ManifestParseError):
        go_mod.parse(manifest)
