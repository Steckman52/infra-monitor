import json
from pathlib import Path

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency, ParsedManifest


def parse(path: Path) -> ParsedManifest:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("file is empty")
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError, OSError) as exc:
        raise ManifestParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestParseError("package.json does not contain a JSON object")

    name = data.get("name")
    deps_raw = data.get("dependencies") or {}
    dependencies = [
        ParsedDependency(name=dep_name, declared_version=dep_version)
        for dep_name, dep_version in deps_raw.items()
    ]
    return ParsedManifest(name=name, dependencies=dependencies)
