import json
from pathlib import Path

from src.scanning.parsed_manifest import (
    ManifestParseError,
    ParsedDependency,
    ParsedManifest,
    read_manifest_text,
)


def parse(path: Path) -> ParsedManifest:
    try:
        text = read_manifest_text(path)
        if not text.strip():
            raise ValueError("file is empty")
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError, OSError, RecursionError) as exc:
        raise ManifestParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestParseError("composer.json does not contain a JSON object")

    name = data.get("name")

    # `require-dev` alongside `require` for the same reason package.json
    # reads devDependencies: PHPUnit or a static analyser pinned to
    # different majors across services is a real conflict worth seeing.
    collected: dict[str, str | None] = {}
    for section in ("require", "require-dev"):
        require_raw = data.get(section) or {}
        if not isinstance(require_raw, dict):
            raise ManifestParseError(f"composer.json '{section}' is not an object")
        for dep_name, dep_version in require_raw.items():
            if dep_name == "php" or dep_name.startswith("ext-"):
                # Runtime/extension constraints, not packages.
                continue
            collected.setdefault(
                dep_name, dep_version if isinstance(dep_version, str) else None
            )

    dependencies = [
        ParsedDependency(name=dep_name, declared_version=dep_version)
        for dep_name, dep_version in collected.items()
    ]
    return ParsedManifest(name=name, dependencies=dependencies)
