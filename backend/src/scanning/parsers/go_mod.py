import re
from pathlib import Path

from src.scanning.parsed_manifest import ManifestParseError, ParsedDependency, ParsedManifest

_MODULE_RE = re.compile(r"^module\s+(\S+)")
_REQUIRE_ENTRY_RE = re.compile(r"^(\S+)\s+(\S+)")


def parse(path: Path) -> ParsedManifest:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ManifestParseError(f"Cannot read file: {exc}") from exc

    if not text.strip():
        raise ManifestParseError("file is empty")

    module_path: str | None = None
    dependencies: list[ParsedDependency] = []
    in_require_block = False

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("//"):
            continue

        module_match = _MODULE_RE.match(line)
        if module_match:
            module_path = module_match.group(1)
            continue

        if line.startswith("require") and line.endswith("("):
            in_require_block = True
            continue

        if in_require_block:
            if line == ")":
                in_require_block = False
                continue
            entry_match = _REQUIRE_ENTRY_RE.match(line)
            if entry_match:
                dependencies.append(
                    ParsedDependency(name=entry_match.group(1), declared_version=entry_match.group(2))
                )
            continue

        if line.startswith("require "):
            entry_match = _REQUIRE_ENTRY_RE.match(line[len("require "):])
            if entry_match:
                dependencies.append(
                    ParsedDependency(name=entry_match.group(1), declared_version=entry_match.group(2))
                )

    if module_path is None:
        raise ManifestParseError("go.mod is missing a 'module' directive")

    name = module_path.rstrip("/").rsplit("/", 1)[-1]
    return ParsedManifest(name=name, dependencies=dependencies)
