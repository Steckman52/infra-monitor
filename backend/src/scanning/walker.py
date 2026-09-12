import os
from collections.abc import Iterator
from pathlib import Path

EXCLUDED_DIR_NAMES = {
    "node_modules",
    "vendor",
    "target",
    ".venv",
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


def find_manifests(root: Path) -> Iterator[tuple[Path, str]]:
    """Walk `root`, yielding (manifest_path, ecosystem) for each supported manifest.

    Prunes EXCLUDED_DIR_NAMES from the walk in-place (FR-006) so the walker never
    descends into dependency-installation directories at all.
    """
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        for filename in filenames:
            ecosystem = MANIFEST_ECOSYSTEMS.get(filename)
            if ecosystem is not None:
                yield Path(dirpath) / filename, ecosystem


def find_docker_compose_files(root: Path) -> Iterator[Path]:
    """Walk `root`, yielding every file literally named `docker-compose.yml`
    (research.md §5, feature 002) — same exclusion pruning as find_manifests."""
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        dirnames[:] = [d for d in dirnames if d not in EXCLUDED_DIR_NAMES]
        if "docker-compose.yml" in filenames:
            yield Path(dirpath) / "docker-compose.yml"
