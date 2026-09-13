from dataclasses import dataclass, field
from pathlib import Path

import yaml

from src.scanning.parsed_manifest import ManifestParseError


@dataclass
class ComposeServiceBlock:
    name: str
    build_context: Path | None
    image: str | None
    networks: list[str] = field(default_factory=list)
    depends_on: list[str] = field(default_factory=list)


@dataclass
class ParsedCompose:
    services: list[ComposeServiceBlock]


def _resolve_build_context(build_value, compose_dir: Path) -> Path | None:
    if isinstance(build_value, str):
        context_str = build_value
    elif isinstance(build_value, dict):
        context_str = build_value.get("context")
        if context_str is None:
            return None
    else:
        return None
    return (compose_dir / context_str).resolve()


def _normalize_names(value) -> list[str]:
    """Compose allows several fields (networks, depends_on) as either a
    list of names or a mapping keyed by name (research.md §3)."""
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v) for v in value]
    if isinstance(value, dict):
        return [str(k) for k in value]
    return []


def parse(path: Path) -> ParsedCompose:
    try:
        text = path.read_text(encoding="utf-8")
        if not text.strip():
            raise ValueError("file is empty")
        data = yaml.safe_load(text)
    except (yaml.YAMLError, ValueError, OSError) as exc:
        raise ManifestParseError(f"Invalid YAML: {exc}") from exc

    if not isinstance(data, dict):
        raise ManifestParseError("docker-compose.yml does not contain a mapping")

    services_raw = data.get("services") or {}
    if not isinstance(services_raw, dict):
        raise ManifestParseError("docker-compose.yml's 'services' is not a mapping")
    compose_dir = path.parent

    services = []
    for name, block in services_raw.items():
        block = block or {}
        if not isinstance(block, dict):
            raise ManifestParseError(f"docker-compose.yml service '{name}' is not a mapping")
        services.append(
            ComposeServiceBlock(
                name=str(name),
                build_context=_resolve_build_context(block.get("build"), compose_dir),
                image=block.get("image"),
                networks=_normalize_names(block.get("networks")),
                depends_on=_normalize_names(block.get("depends_on")),
            )
        )

    return ParsedCompose(services=services)
