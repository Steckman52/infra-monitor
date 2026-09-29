import re
import xml.etree.ElementTree as ET
from pathlib import Path

from src.scanning.parsed_manifest import (
    ManifestParseError,
    ParsedDependency,
    ParsedManifest,
    read_manifest_text,
)

_PROPERTY_REF_RE = re.compile(r"\$\{([^}]+)\}")

# A property may be defined in terms of another. Two passes resolve the
# nesting depth real POMs use; the bound is what stops a self-referential
# property (`<a>${a}</a>`) from looping forever.
_MAX_PROPERTY_PASSES = 2


def _local_tag(tag: str) -> str:
    return tag.split("}", 1)[-1] if "}" in tag else tag


def _text(element, tag_name: str) -> str | None:
    for child in element:
        if _local_tag(child.tag) == tag_name:
            value = (child.text or "").strip()
            return value or None
    return None


def _collect_properties(root) -> dict[str, str]:
    """The `<properties>` block of this POM only. Values inherited from a
    parent POM are deliberately not chased: the parent is a separate file
    that may live outside the scanned tree, and inventing a version is worse
    than reporting it as unreadable (002 FR-004)."""
    properties: dict[str, str] = {}
    for child in root:
        if _local_tag(child.tag) != "properties":
            continue
        for prop in child:
            properties[_local_tag(prop.tag)] = (prop.text or "").strip()
    return properties


def _resolve(value: str | None, properties: dict[str, str]) -> str | None:
    """Substitute `${...}` references that this POM defines. An unresolved
    reference is left verbatim on purpose -- it then reads as "not
    comparable" downstream, which is the truth, rather than being silently
    dropped or guessed at."""
    if value is None or "${" not in value:
        return value
    for _ in range(_MAX_PROPERTY_PASSES):
        replaced = _PROPERTY_REF_RE.sub(
            lambda m: properties.get(m.group(1), m.group(0)), value
        )
        if replaced == value:
            break
        value = replaced
    return value


def parse(path: Path) -> ParsedManifest:
    try:
        text = read_manifest_text(path)
        if not text.strip():
            raise ValueError("file is empty")
        root = ET.fromstring(text)
    except (ET.ParseError, ValueError, OSError) as exc:
        raise ManifestParseError(f"Invalid XML: {exc}") from exc

    group_id = _text(root, "groupId")
    artifact_id = _text(root, "artifactId")
    properties = _collect_properties(root)

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
            dep_version = _resolve(_text(dependency, "version"), properties)
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
