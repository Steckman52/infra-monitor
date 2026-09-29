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


def test_property_placeholder_versions_are_resolved(tmp_path):
    # Real Maven modules rarely inline a version; they point at a property.
    # Left unresolved, every such dependency reads as "not comparable" and
    # the compatibility view has nothing to work with.
    manifest = tmp_path / "pom.xml"
    manifest.write_text(
        """<project>
  <groupId>com.example</groupId>
  <artifactId>gateway</artifactId>
  <properties>
    <okhttp.version>5.0.0</okhttp.version>
  </properties>
  <dependencies>
    <dependency>
      <groupId>com.squareup.okhttp3</groupId>
      <artifactId>okhttp</artifactId>
      <version>${okhttp.version}</version>
    </dependency>
  </dependencies>
</project>""",
        encoding="utf-8",
    )

    result = pom_xml.parse(manifest)

    assert result.dependencies[0].declared_version == "5.0.0"


def test_property_defined_via_another_property_is_resolved(tmp_path):
    manifest = tmp_path / "pom.xml"
    manifest.write_text(
        """<project>
  <groupId>com.example</groupId>
  <artifactId>gateway</artifactId>
  <properties>
    <base.version>3.1.4</base.version>
    <lib.version>${base.version}</lib.version>
  </properties>
  <dependencies>
    <dependency>
      <artifactId>some-lib</artifactId>
      <version>${lib.version}</version>
    </dependency>
  </dependencies>
</project>""",
        encoding="utf-8",
    )

    result = pom_xml.parse(manifest)

    assert result.dependencies[0].declared_version == "3.1.4"


def test_unknown_property_is_left_verbatim_not_guessed(tmp_path):
    # Inherited from a parent POM that may not even be in the scanned tree.
    # Leaving the reference intact keeps it honestly "not comparable".
    manifest = tmp_path / "pom.xml"
    manifest.write_text(
        """<project>
  <groupId>com.example</groupId>
  <artifactId>gateway</artifactId>
  <dependencies>
    <dependency>
      <artifactId>spring-core</artifactId>
      <version>${spring.version}</version>
    </dependency>
  </dependencies>
</project>""",
        encoding="utf-8",
    )

    result = pom_xml.parse(manifest)

    assert result.dependencies[0].declared_version == "${spring.version}"


def test_self_referential_property_terminates(tmp_path):
    manifest = tmp_path / "pom.xml"
    manifest.write_text(
        """<project>
  <groupId>com.example</groupId>
  <artifactId>gateway</artifactId>
  <properties>
    <loop.version>${loop.version}</loop.version>
  </properties>
  <dependencies>
    <dependency>
      <artifactId>some-lib</artifactId>
      <version>${loop.version}</version>
    </dependency>
  </dependencies>
</project>""",
        encoding="utf-8",
    )

    result = pom_xml.parse(manifest)  # must not hang

    assert result.dependencies[0].declared_version == "${loop.version}"
