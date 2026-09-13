from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from src.models.adr_import_issue import AdrImportIssue
from src.models.adr_record import AdrRecord
from src.models.adr_relationship import AdrRelationship
from src.models.adr_service_association import AdrServiceAssociation
from src.models.dependency import Dependency
from src.models.external_node import ExternalNode
from src.models.scan_issue import ScanIssue
from src.models.scan_metadata import record_scan
from src.models.service import Service
from src.models.service_connection import ServiceConnection
from src.scanning import name_resolution
from src.scanning.adr_relationships import resolve_relationships
from src.scanning.adr_secrets import check_for_secrets
from src.scanning.connection_graph import build_graph_for_compose
from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import adr_markdown, composer_json, docker_compose, go_mod, package_json, pom_xml, requirements_txt
from src.scanning.walker import find_adr_files, find_docker_compose_files, find_manifests

_PARSERS = {
    "node": package_json.parse,
    "java": pom_xml.parse,
    "python": requirements_txt.parse,
    "go": go_mod.parse,
    "php": composer_json.parse,
}


@dataclass
class ScanSummary:
    services_found: int
    issues_found: int
    unreachable_roots: list[str]
    adrs_found: int = 0


def _unparsable_issue(exc: ManifestParseError, path: Path, repository_path: str, now: datetime) -> ScanIssue:
    """Shared shape for the two 'a manifest-like file failed to parse'
    cases (a package manifest, or a docker-compose.yml) -- isolates the
    failure as one ScanIssue row instead of aborting the scan."""
    return ScanIssue(
        manifest_path=str(path),
        repository_path=repository_path,
        issue_type="unparsable",
        reason=exc.reason,
        detected_at=now,
    )


def _scan_manifests(
    root_path: Path, existing_names: set[str], now: datetime
) -> tuple[list[Service], list[ScanIssue]]:
    """FR-007/FR-008/FR-009: parse every manifest under `root_path`,
    isolating a parse failure or incomplete data as its own ScanIssue
    without aborting the rest of the scan."""
    services_to_add: list[Service] = []
    issues_to_add: list[ScanIssue] = []

    for manifest_path, ecosystem in find_manifests(root_path):
        repository_path = str(manifest_path.parent)
        try:
            parsed = _PARSERS[ecosystem](manifest_path)
        except ManifestParseError as exc:
            issues_to_add.append(_unparsable_issue(exc, manifest_path, repository_path, now))
            continue

        resolved_name = name_resolution.resolve_name(parsed.name, manifest_path, existing_names)
        existing_names.add(resolved_name)

        service = Service(
            name=resolved_name,
            ecosystem=ecosystem,
            repository_path=repository_path,
            manifest_path=str(manifest_path),
            is_complete=parsed.is_complete,
            last_scanned_at=now,
        )
        service.dependencies = [
            Dependency(name=dep.name, declared_version=dep.declared_version)
            for dep in parsed.dependencies
        ]
        services_to_add.append(service)

        if not parsed.is_complete:
            # FR-009: still registered, but flagged and explained.
            issues_to_add.append(
                ScanIssue(
                    manifest_path=str(manifest_path),
                    repository_path=repository_path,
                    issue_type="incomplete_data",
                    reason=parsed.incomplete_reason or "Manifest is missing required data",
                    service=service,
                    detected_at=now,
                )
            )

    return services_to_add, issues_to_add


def _scan_compose(
    compose_files: list[Path], services_by_build_context: dict[Path, Service], now: datetime
) -> tuple[list[ExternalNode], list[ServiceConnection], list[ScanIssue]]:
    """002 FR-009/FR-013: build the connection graph from every
    docker-compose.yml found, isolating a parse failure the same way
    manifest failures are."""
    external_nodes_to_add: list[ExternalNode] = []
    connections_to_add: list[ServiceConnection] = []
    issues_to_add: list[ScanIssue] = []

    for compose_path in compose_files:
        repository_path = str(compose_path.parent)
        try:
            parsed_compose = docker_compose.parse(compose_path)
        except ManifestParseError as exc:
            issues_to_add.append(_unparsable_issue(exc, compose_path, repository_path, now))
            continue

        result = build_graph_for_compose(
            parsed_compose, compose_path, repository_path, services_by_build_context
        )
        external_nodes_to_add.extend(result.external_nodes)
        connections_to_add.extend(result.connections)

    return external_nodes_to_add, connections_to_add, issues_to_add


def _scan_adrs(adr_files: list[Path], now: datetime) -> tuple[list[AdrRecord], list[AdrImportIssue]]:
    """004 FR-002/FR-008: every docs/adr/*.md is one ADR; a parse failure
    (no title) is isolated as its own AdrImportIssue, never a ScanIssue --
    kept in a dedicated table so this scan and the registry scan can never
    clobber each other's issue history (004 ADR 0007-in-spirit)."""
    adrs_to_add: list[AdrRecord] = []
    adr_issues_to_add: list[AdrImportIssue] = []

    for adr_path in adr_files:
        # repository root = grandparent of docs/adr (research.md §7).
        repository_path = str(adr_path.parent.parent.parent)
        try:
            fields = adr_markdown.parse(adr_path)
        except ManifestParseError as exc:
            adr_issues_to_add.append(
                AdrImportIssue(path=str(adr_path), reason=exc.reason, detected_at=now)
            )
            continue

        adrs_to_add.append(
            AdrRecord(
                title=fields.title,
                raw_status=fields.raw_status,
                normalized_status=fields.normalized_status,
                date=fields.date,
                source_path=str(adr_path),
                repository_path=repository_path,
                content=fields.content,
                has_secret_warning=check_for_secrets(fields.content),
            )
        )

    return adrs_to_add, adr_issues_to_add


def _resolve_adr_associations(
    adrs_to_add: list[AdrRecord], services_to_add: list[Service]
) -> list[AdrServiceAssociation]:
    """004 FR-006: associate each ADR with every service registered under
    its own repository root (research.md §7) -- derived only from
    in-memory objects, since none of this has an id yet before the
    transaction below commits."""
    associations_to_add: list[AdrServiceAssociation] = []
    for adr in adrs_to_add:
        repo_root = Path(adr.repository_path).resolve()
        for service in services_to_add:
            service_path = Path(service.repository_path).resolve()
            if service_path == repo_root or repo_root in service_path.parents:
                association = AdrServiceAssociation()
                association.adr = adr
                association.service = service
                associations_to_add.append(association)
    return associations_to_add


def run_scan(session: Session, roots: list[str]) -> ScanSummary:
    """Scan `roots` for manifests, docker-compose.yml files, and
    docs/adr/*.md files, replacing the registry's, external nodes',
    connections', and ADRs' contents in one transaction (research.md
    §8/002 §1/004 §1-2), so a re-scan always reflects the current state
    of the repositories (FR-014 / 002 FR-015 / 004 FR-012).
    """
    now = datetime.now(timezone.utc)
    existing_names: set[str] = set()
    services_to_add: list[Service] = []
    issues_to_add: list[ScanIssue] = []
    unreachable_roots: list[str] = []
    compose_files: list[Path] = []
    adr_files: list[Path] = []

    for root in roots:
        root_path = Path(root)
        if not root_path.is_dir():
            # FR-010: report each unreachable root without aborting the rest.
            unreachable_roots.append(root)
            issues_to_add.append(
                ScanIssue(
                    manifest_path=root,
                    repository_path=root,
                    issue_type="unreachable_path",
                    reason=f"Root path does not exist or is not a directory: {root}",
                    detected_at=now,
                )
            )
            continue

        root_services, root_issues = _scan_manifests(root_path, existing_names, now)
        services_to_add.extend(root_services)
        issues_to_add.extend(root_issues)

        compose_files.extend(find_docker_compose_files(root_path))
        adr_files.extend(find_adr_files(root_path))

    # 002 FR-009: match docker-compose service blocks to the services just
    # scanned above by resolved build-context path (in-memory; these Service
    # objects have no id yet, but connection_graph assigns via relationship,
    # not raw FK, so that's fine).
    services_by_build_context = {
        Path(service.repository_path).resolve(): service for service in services_to_add
    }
    external_nodes_to_add, connections_to_add, compose_issues = _scan_compose(
        compose_files, services_by_build_context, now
    )
    issues_to_add.extend(compose_issues)

    adrs_to_add, adr_issues_to_add = _scan_adrs(adr_files, now)
    relationships_to_add = resolve_relationships(adrs_to_add)
    associations_to_add = _resolve_adr_associations(adrs_to_add, services_to_add)

    # Replace all prior scan results in one transaction. Children first, since
    # SQLite enforces FK constraints and bulk deletes bypass ORM cascades.
    session.query(ServiceConnection).delete()
    session.query(ScanIssue).delete()
    session.query(Dependency).delete()
    session.query(ExternalNode).delete()
    session.query(Service).delete()
    session.query(AdrImportIssue).delete()
    session.query(AdrRelationship).delete()
    session.query(AdrServiceAssociation).delete()
    session.query(AdrRecord).delete()
    session.add_all(services_to_add)
    session.add_all(issues_to_add)
    session.add_all(external_nodes_to_add)
    session.add_all(connections_to_add)
    session.add_all(adrs_to_add)
    session.add_all(adr_issues_to_add)
    session.add_all(relationships_to_add)
    session.add_all(associations_to_add)
    record_scan(session, "registry", now)
    session.commit()

    return ScanSummary(
        services_found=len(services_to_add),
        issues_found=len(issues_to_add),
        unreachable_roots=unreachable_roots,
        adrs_found=len(adrs_to_add),
    )
