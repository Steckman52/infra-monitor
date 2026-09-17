import os
from collections.abc import Iterator
from pathlib import Path

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
}

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
MAX_DIRECTORIES_WALKED = 50_000


def _walk_with_cap(root: Path) -> Iterator[tuple[str, list[str], list[str]]]:
    for count, entry in enumerate(os.walk(root, topdown=True), start=1):
        yield entry
        if count >= MAX_DIRECTORIES_WALKED:
            break


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


def find_docker_compose_files(root: Path) -> Iterator[Path]:
    """Walk `root`, yielding every file literally named `docker-compose.yml`
    (research.md §5, feature 002) — same exclusion pruning as find_manifests."""
    for dirpath, dirnames, filenames in _walk_with_cap(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        if "docker-compose.yml" in filenames:
            yield Path(dirpath) / "docker-compose.yml"


LOG_FILE_EXTENSIONS = {".log", ".txt", ""}


def find_log_files(root: Path) -> Iterator[Path]:
    """Walk `root`, yielding files with extension `.log`, `.txt`, or no
    extension (003 FR-002) — same exclusion pruning as find_manifests.
    Other extensions (e.g. compressed/rotated logs) are never yielded."""
    for dirpath, dirnames, filenames in _walk_with_cap(root):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in filenames:
            path = Path(dirpath) / filename
            if path.suffix.lower() in LOG_FILE_EXTENSIONS:
                yield path


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
