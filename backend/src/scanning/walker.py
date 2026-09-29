import os
import re
from collections.abc import Iterator
from pathlib import Path

from src import config

EXCLUDED_DIR_NAMES = {
    "node_modules",
    "vendor",
    "target",
    ".venv",
    "venv",
    "env",
    "site-packages",
    "__pycache__",
    ".git",
    # Credential stores. Nothing in them is a manifest, an ADR or a log, and
    # a scan rooted at a home directory would otherwise walk straight into
    # private keys and cloud credentials.
    ".ssh",
    ".aws",
    ".gnupg",
} | set(config.EXTRA_EXCLUDED_DIRS)

MANIFEST_ECOSYSTEMS = {
    "package.json": "node",
    "pom.xml": "java",
    "requirements.txt": "python",
    "go.mod": "go",
    "composer.json": "php",
}

# Bounds the cost of pointing a scan at an accidentally enormous root (e.g. a
# drive root): without this, os.walk's cost scales with every directory in
# the tree, blocking the request and holding the scan's write transaction
# open for the duration. 50,000 directories comfortably covers any real
# repository or log tree this tool is meant to scan.
MAX_DIRECTORIES_WALKED = config.MAX_DIRECTORIES_WALKED


class WalkTruncated(Exception):
    """Raised when a walk hit MAX_DIRECTORIES_WALKED.

    The cap used to just `break`, which meant a scan of a tree larger than
    the cap returned a subset of the services and reported success -- the
    operator concluded a service did not exist when the walker had simply
    stopped early. For a tool whose entire job is "what do we actually
    have", under-reporting silently is the worst available behaviour, so
    the truncation is now loud and the caller turns it into a scan issue.
    """

    def __init__(self, root: Path) -> None:
        super().__init__(
            f"Stopped after {MAX_DIRECTORIES_WALKED:,} directories under {root}. "
            "Results are incomplete -- scan narrower roots."
        )
        self.root = root


def _walk_with_cap(root: Path) -> Iterator[tuple[str, list[str], list[str]]]:
    for count, entry in enumerate(os.walk(root, topdown=True), start=1):
        yield entry
        if count >= MAX_DIRECTORIES_WALKED:
            raise WalkTruncated(root)


def find_manifests(root: Path) -> Iterator[tuple[Path, str]]:
    """Walk `root`, yielding (manifest_path, ecosystem) for each supported manifest.

    Prunes EXCLUDED_DIR_NAMES from the walk in-place (FR-006) so the walker never
    descends into dependency-installation directories at all.
    """
    for dirpath, dirnames, filenames in _walk_with_cap(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in filenames:
            ecosystem = MANIFEST_ECOSYSTEMS.get(filename)
            if ecosystem is not None:
                yield Path(dirpath) / filename, ecosystem


# `compose.yaml` is the name the current Compose specification prefers, and
# `.yaml` spellings and `docker-compose.prod.yml`-style variants are all
# common in real repositories. Matching only the one exact legacy filename
# meant such a repository appeared to have no container topology at all.
_COMPOSE_NAME_RE = re.compile(
    r"^(?:docker-)?compose(?:[.-][A-Za-z0-9_-]+)?\.ya?ml$", re.IGNORECASE
)


def is_compose_file(filename: str) -> bool:
    return bool(_COMPOSE_NAME_RE.match(filename))


def find_docker_compose_files(root: Path) -> Iterator[Path]:
    """Walk `root`, yielding every Compose file (research.md §5, feature
    002) — same exclusion pruning as find_manifests."""
    for dirpath, dirnames, filenames in _walk_with_cap(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in sorted(filenames):
            if is_compose_file(filename):
                yield Path(dirpath) / filename


# `.jsonl`/`.ndjson` are the conventional extensions for JSON-lines logs --
# the format most modern services emit. `.out`/`.err` cover catalina.out,
# nohup.out and redirected stdout/stderr.
LOG_FILE_EXTENSIONS = {".log", ".txt", ".jsonl", ".ndjson", ".out", ".err"}

# Apache and some older tooling write an extensionless `error_log`/`access_log`.
# Named explicitly rather than by re-admitting all extensionless files, which
# is what previously pulled in `.env`, `id_rsa` and `credentials`.
_LOG_FILENAMES = {"error_log", "access_log", "messages", "syslog"}

# Rotated logs: `app.log.1`, `app.log.2024-01-01`. Matching these is the
# difference between analysing one day and analysing the history that is
# actually on disk. Compressed rotations (`.gz`, `.zip`, `.bz2`, `.xz`) are
# deliberately still skipped -- they are not readable as text.
_ROTATED_LOG_RE = re.compile(r"\.log\.[A-Za-z0-9._-]+$", re.IGNORECASE)
_COMPRESSED_SUFFIXES = {".gz", ".zip", ".bz2", ".xz", ".zst", ".7z"}


def is_log_file(filename: str) -> bool:
    """003 FR-002. Extensionless files are NOT logs, however tempting the
    generalisation: that rule admitted `.env`, `id_rsa`, `credentials`,
    `.npmrc`, `.bash_history` and `.pgpass`, whose contents were then read
    in full, persisted, and served back over the API. A log scanner has no
    business reading a private key, and the cost of the stricter rule is
    only that a genuinely extensionless log file is skipped."""
    path = Path(filename)
    if path.suffix.lower() in _COMPRESSED_SUFFIXES:
        return False
    if path.suffix.lower() in LOG_FILE_EXTENSIONS:
        return True
    if filename.lower() in _LOG_FILENAMES:
        return True
    return bool(_ROTATED_LOG_RE.search(filename))


def find_log_files(root: Path) -> Iterator[Path]:
    """Walk `root`, yielding readable log files (003 FR-002) — same
    exclusion pruning as find_manifests."""
    for dirpath, dirnames, filenames in _walk_with_cap(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in filenames:
            if is_log_file(filename):
                yield Path(dirpath) / filename


def find_adr_files(root: Path) -> Iterator[Path]:
    """Walk `root`, yielding every Markdown file directly inside a
    `docs/adr` directory (004 FR-002) — same exclusion pruning as
    find_manifests. Non-Markdown files in that same directory (e.g. a
    diagram) are silently excluded, not reported."""
    for dirpath, dirnames, filenames in _walk_with_cap(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        dir_path = Path(dirpath)
        if dir_path.name == "adr" and dir_path.parent.name == "docs":
            for filename in filenames:
                if filename.lower().endswith(".md"):
                    yield dir_path / filename
