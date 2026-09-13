import pytest

from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import requirements_txt


def test_parses_pinned_and_range_dependencies(tmp_path):
    manifest = tmp_path / "requirements.txt"
    manifest.write_text(
        "flask==2.3.2\nrequests>=2.31.0\n# a comment\n-r other.txt\n-e .\n",
        encoding="utf-8",
    )

    result = requirements_txt.parse(manifest)

    assert result.name is None  # requirements.txt never carries a name (FR-004 rule 2)
    names_versions = {(d.name, d.declared_version) for d in result.dependencies}
    assert ("flask", "==2.3.2") in names_versions
    assert ("requests", ">=2.31.0") in names_versions
    assert len(result.dependencies) == 2  # comment/-r/-e lines are skipped, not deps


def test_non_utf8_bytes_raise_manifest_parse_error(tmp_path):
    manifest = tmp_path / "requirements.txt"
    manifest.write_bytes(b"flask==2.3.2\n\xff\xfe invalid utf-8 bytes")

    with pytest.raises(ManifestParseError):
        requirements_txt.parse(manifest)
