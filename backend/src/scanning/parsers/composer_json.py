import json
from pathlib import Path

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency, ParsedManifest


def parse(path: Path) -> ParsedManifest:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("file is empty")
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError, OSError, RecursionError) as exc:
        raise ManifestParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestParseError("composer.json does not contain a JSON object")

    name = data.get("name")
    require_raw = data.get("require") or {}
    if not isinstance(require_raw, dict):
        raise ManifestParseError("composer.json 'require' is not an object")
    dependencies = [
        ParsedDependency(
            name=dep_name,
            declared_version=dep_version if isinstance(dep_version, str) else None,
        )
        for dep_name, dep_version in require_raw.items()
        if dep_name != "php"  # a runtime version constraint, not a real dependency
    ]
    return ParsedManifest(name=name, dependencies=dependencies)
