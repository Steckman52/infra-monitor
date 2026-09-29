import re
from pathlib import Path

from src.scanning.parsed_manifest import (
    ManifestParseError,
    ParsedDependency,
    ParsedManifest,
    read_manifest_text,
)

# The name may carry extras (`requests[security]`), which are not part of the
# project name and must not stop the version being read -- previously the
# name class stopped at `[` and the pin was silently lost, reporting a
# pinned dependency as version-unknown.
_DEP_RE = re.compile(
    r"^(?P<name>[A-Za-z0-9._-]+)"
    r"(?:\[[^\]]*\])?"
    r"\s*(?P<version>(?:==|>=|<=|~=|!=|===|>|<)\s*[^\s;#]+)?"
)

# A requirement given as a URL or VCS reference. These have no reliable
# package name in the line at all -- reading one as a dependency produced a
# phantom dependency literally named `git` or `https`, which then appeared
# in the cross-service compatibility table as if it were real.
_URL_REQUIREMENT_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*://|^(?:git|hg|bzr|svn)\+")

# `#egg=name` names the package a VCS requirement installs, so a URL
# requirement can still be attributed when the author supplied it.
_EGG_RE = re.compile(r"[#&]egg=([A-Za-z0-9._-]+)")

_NORMALIZE_RE = re.compile(r"[-_.]+")


def canonicalize_name(name: str) -> str:
    """PEP 503 canonical form: lowercase, runs of `-_.` collapsed to `-`.

    `Flask` and `flask`, `PyYAML` and `pyyaml`, `python-dateutil` and
    `python_dateutil` are the same PyPI project. Grouping on the raw string
    split them into separate rows, and because each row then held only one
    service, the compatibility view discarded them as unshared -- so a real
    version conflict between two services was never shown at all.
    """
    return _NORMALIZE_RE.sub("-", name).lower()


def parse(path: Path) -> ParsedManifest:
    text = read_manifest_text(path)

    if not text.strip():
        raise ManifestParseError("file is empty")

    # A `\`-continued requirement is one logical line.
    text = text.replace("\\\n", " ")

    dependencies: list[ParsedDependency] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r", "-c", "-e", "--", ".", "/")):
            # Include directives, editable and local-path installs: not a
            # dependency declaration (research.md §3), not a parse failure.
            continue

        if _URL_REQUIREMENT_RE.match(line):
            egg = _EGG_RE.search(line)
            if egg is None:
                continue  # unattributable, and a guess here is worse than a gap
            dependencies.append(
                ParsedDependency(name=canonicalize_name(egg.group(1)), declared_version=None)
            )
            continue

        match = _DEP_RE.match(line)
        if not match:
            continue
        version = match.group("version")
        dependencies.append(
            ParsedDependency(
                name=canonicalize_name(match.group("name")),
                declared_version=version.strip() if version else None,
            )
        )

    # requirements.txt never carries a project/service name (FR-004 rule 2).
    return ParsedManifest(name=None, dependencies=dependencies)
