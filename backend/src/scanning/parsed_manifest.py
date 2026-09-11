from dataclasses import dataclass, field


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
