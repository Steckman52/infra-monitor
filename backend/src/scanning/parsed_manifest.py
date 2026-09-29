from dataclasses import dataclass, field
from pathlib import Path

# Manifests and ADRs are small by nature -- a large pom.xml is a few hundred
# KB. Reading one is whole-file, and JSON/XML/YAML parsing costs several
# times the text size again, so an accidental (or hostile) giant file here
# is a memory spike with no legitimate use. Generous enough that no real
# manifest will ever reach it.
MAX_MANIFEST_BYTES = 16 * 1024 * 1024


@dataclass
class ParsedDependency:
    name: str
    declared_version: str | None


@dataclass
class ParsedManifest:
    """Result of parsing one manifest file, before name resolution (FR-004) is applied."""

    name: str | None
    dependencies: list[ParsedDependency] = field(default_factory=list)
    is_complete: bool = True
    incomplete_reason: str | None = None


class ManifestParseError(Exception):
    """Raised when a manifest's content cannot be parsed at all (FR-007/FR-008)."""

    def __init__(self, reason: str):
        super().__init__(reason)
        self.reason = reason


def read_manifest_text(path: Path) -> str:
    """Read a manifest/ADR as text, refusing anything implausibly large.

    Shared by every parser so the size guard cannot be forgotten in one of
    them -- the log scanner has its own, larger limit, since log files are
    legitimately big.
    """
    try:
        size = path.stat().st_size
    except OSError as exc:
        raise ManifestParseError(f"Cannot read file: {exc}") from exc

    if size > MAX_MANIFEST_BYTES:
        raise ManifestParseError(
            f"File is {size // 1_000_000} MB, above the "
            f"{MAX_MANIFEST_BYTES // 1_000_000} MB limit for a manifest"
        )

    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError, MemoryError) as exc:
        raise ManifestParseError(f"Cannot read file: {exc}") from exc
