import re
from pathlib import Path

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency, ParsedManifest

_DEP_RE = re.compile(r"^([A-Za-z0-9._-]+)\s*((?:==|>=|<=|~=|!=|>|<)\s*[^\s;#]+)?")


def parse(path: Path) -> ParsedManifest:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestParseError(f"Cannot read file: {exc}") from exc

    if not text.strip():
        raise ManifestParseError("file is empty")

    dependencies: list[ParsedDependency] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r", "-e", "--")):
            # Not a dependency declaration (include directive, editable install,
            # or a pip option) — skipped per research.md §3, not a parse failure.
            continue
        match = _DEP_RE.match(line)
        if not match:
            continue
        package_name = match.group(1)
        version = match.group(2)
        dependencies.append(
            ParsedDependency(
                name=package_name,
                declared_version=version.strip() if version else None,
            )
        )

    # requirements.txt never carries a project/service name (FR-004 rule 2).
    return ParsedManifest(name=None, dependencies=dependencies)
