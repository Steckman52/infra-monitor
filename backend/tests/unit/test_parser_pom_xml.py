import pytest

from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import pom_xml


def test_parses_group_and_artifact_id_and_dependencies(tmp_path):
    manifest = tmp_path / "pom.xml"
    manifest.write_text(
        """<project>
  <groupId>com.example</groupId>
  <artifactId>orders-service</artifactId>
  <dependencies>
    <dependency>
      <groupId>org.springframework</groupId>
      <artifactId>spring-core</artifactId>
      <version>5.3.20</version>
    </dependency>
  </dependencies>
</project>""",
        encoding="utf-8",
    )

    result = pom_xml.parse(manifest)

    assert result.name == "com.example:orders-service"
    assert result.is_complete is True
    assert result.dependencies[0].name == "org.springframework:spring-core"
    assert result.dependencies[0].declared_version == "5.3.20"


def test_missing_artifact_id_marks_incomplete(tmp_path):
    manifest = tmp_path / "pom.xml"
    manifest.write_text(
        """<project>
  <groupId>com.example</groupId>
  <packaging>pom</packaging>
</project>""",
        encoding="utf-8",
    )

    result = pom_xml.parse(manifest)

    assert result.is_complete is False
    assert result.incomplete_reason


def test_invalid_xml_raises_manifest_parse_error(tmp_path):
    manifest = tmp_path / "pom.xml"
    manifest.write_text("<project><groupId>com.example</groupId>", encoding="utf-8")

    with pytest.raises(ManifestParseError):
        pom_xml.parse(manifest)
