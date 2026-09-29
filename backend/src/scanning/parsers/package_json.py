import json
from pathlib import Path

from src.scanning.parsed_manifest import (
    ManifestParseError,
    ParsedDependency,
    ParsedManifest,
    read_manifest_text,
)

# All of these are dependencies the service itself declares directly (001
# FR: "direct dependencies"). Build tooling lives in devDependencies, and
# two services pinned to different major versions of the same bundler or
# type-checker is exactly the conflict this tool exists to surface --
# skipping them also meant any app with only devDependencies (a Vite or
# Laravel frontend, say) registered as having no dependencies at all.
# peerDependencies are excluded: they constrain a consumer, they are not
# something this service installs.
_DEPENDENCY_SECTIONS = ("dependencies", "devDependencies", "optionalDependencies")


def parse(path: Path) -> ParsedManifest:
    try:
        text = read_manifest_text(path)
        if not text.strip():
            raise ValueError("file is empty")
        data = json.loads(text)
    except (json.JSONDecodeError, ValueError, OSError, RecursionError) as exc:
        raise ManifestParseError(f"Invalid JSON: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestParseError("package.json does not contain a JSON object")

    name = data.get("name")

    # A package can appear in more than one section; the first wins, so a
    # runtime dependency is not overwritten by a dev-time duplicate.
    collected: dict[str, str | None] = {}
    for section in _DEPENDENCY_SECTIONS:
        deps_raw = data.get(section) or {}
        if not isinstance(deps_raw, dict):
            raise ManifestParseError(f"package.json '{section}' is not an object")
        for dep_name, dep_version in deps_raw.items():
            collected.setdefault(
                dep_name, dep_version if isinstance(dep_version, str) else None
            )

    dependencies = [
        ParsedDependency(name=dep_name, declared_version=dep_version)
        for dep_name, dep_version in collected.items()
    ]
    return ParsedManifest(name=name, dependencies=dependencies)
