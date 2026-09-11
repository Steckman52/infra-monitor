import xml.etree.ElementTree as ET
from pathlib import Path

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency, ParsedManifest


def _local_tag(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _text(element, tag_name: str) -> str | None:
    for child in element:
        if _local_tag(child.tag) == tag_name:
            value = (child.text or "").strip()
            return value or None
    return None


def parse(path: Path) -> ParsedManifest:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("file is empty")
        root = ET.fromstring(text)
    except (ET.ParseError, ValueError, OSError) as exc:
        raise ManifestParseError(f"Invalid XML: {exc}") from exc

    group_id = _text(root, "groupId")
    artifact_id = _text(root, "artifactId")

    dependencies: list[ParsedDependency] = []
    for child in root:
        if _local_tag(child.tag) != "dependencies":
            continue
        for dependency in child:
            if _local_tag(dependency.tag) != "dependency":
                continue
            dep_artifact = _text(dependency, "artifactId")
            if not dep_artifact:
                continue
            dep_group = _text(dependency, "groupId")
            dep_version = _text(dependency, "version")
            dep_name = f"{dep_group}:{dep_artifact}" if dep_group else dep_artifact
            dependencies.append(ParsedDependency(name=dep_name, declared_version=dep_version))

    if artifact_id:
        name = f"{group_id}:{artifact_id}" if group_id else artifact_id
        return ParsedManifest(name=name, dependencies=dependencies)

    # FR-009: valid XML but missing <artifactId> (typical of a parent POM) — the
    # service is still registered, just marked incomplete rather than discarded.
    return ParsedManifest(
        name=None,
        dependencies=dependencies,
        is_complete=False,
        incomplete_reason="pom.xml is missing <artifactId> (parent POM?)",
    )
