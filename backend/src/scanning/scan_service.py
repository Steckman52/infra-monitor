from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from src.models.dependency import Dependency
from src.models.scan_issue import ScanIssue
from src.models.service import Service
from src.scanning import name_resolution
from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import composer_json, go_mod, package_json, pom_xml, requirements_txt
from src.scanning.walker import find_manifests

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


def run_scan(session: Session, roots: list[str]) -> ScanSummary:
    """Scan `roots` for manifests and replace the registry's contents in one
    transaction (research.md §8), so a re-scan always reflects the current state
    of the repositories (FR-014).
    """
    now = datetime.now(timezone.utc)
    existing_names: set[str] = set()
    services_to_add: list[Service] = []
    issues_to_add: list[ScanIssue] = []
    unreachable_roots: list[str] = []

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

        for manifest_path, ecosystem in find_manifests(root_path):
            repository_path = str(manifest_path.parent)
            try:
                parsed = _PARSERS[ecosystem](manifest_path)
            except ManifestParseError as exc:
                # FR-007/FR-008: isolate this failure, keep scanning the rest.
                issues_to_add.append(
                    ScanIssue(
                        manifest_path=str(manifest_path),
                        repository_path=repository_path,
                        issue_type="unparsable",
                        reason=exc.reason,
                        detected_at=now,
                    )
                )
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

    # Replace all prior scan results in one transaction. Children first, since
    # SQLite enforces FK constraints and bulk deletes bypass ORM cascades.
    session.query(ScanIssue).delete()
    session.query(Dependency).delete()
    session.query(Service).delete()
    session.add_all(services_to_add)
    session.add_all(issues_to_add)
    session.commit()

    return ScanSummary(
        services_found=len(services_to_add),
        issues_found=len(issues_to_add),
        unreachable_roots=unreachable_roots,
    )
