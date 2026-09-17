import re
from collections import defaultdict
from dataclasses import dataclass

from sqlalchemy.orm import Session

from src.models.dependency import Dependency
from src.models.service import Service

_LEADING_DIGITS_RE = re.compile(r"\D*(\d+)")
_MAJOR_MINOR_RE = re.compile(r"\D*(\d+)\D+(\d+)")


def extract_major_version(declared_version: str | None) -> int | None:
    """FR-003: strip any leading non-digit characters (range operators,
    'v' prefixes, etc.) and return the leading digit run as the major
    version. Returns None when no leading digit run exists at all (FR-004),
    e.g. a build-tool property placeholder or a non-numeric version alias.
    """
    if not declared_version:
        return None
    match = _LEADING_DIGITS_RE.match(declared_version)
    if not match:
        return None
    return int(match.group(1))


def extract_effective_version(declared_version: str | None) -> tuple[int, ...] | None:
    """The unit two declared versions are actually compared on. Per SemVer's
    own rule (https://semver.org/#spec-item-4), while major is 0 the API is
    still unstable and a minor bump is the breaking-change boundary -- so
    comparing major alone would call fastapi>=0.104 and fastapi>=0.115
    "compatible" just because both happen to be pre-1.0. Everything with a
    nonzero major keeps the existing major-only comparison.
    """
    major = extract_major_version(declared_version)
    if major is None:
        return None
    if major != 0:
        return (major,)
    match = _MAJOR_MINOR_RE.match(declared_version)
    return (0, int(match.group(2))) if match else (0,)


def status_for_majors(major_versions: list[int | None]) -> tuple[str, bool]:
    """FR-005: status is 'compatible' when every comparable major matches
    (vacuously true with zero or one comparable entries), or
    'compatibility_risk' when at least two comparable majors differ.
    `has_not_comparable` is tracked independently of that status.
    """
    comparable = [m for m in major_versions if m is not None]
    has_not_comparable = len(comparable) < len(major_versions)
    status = "compatible" if len(set(comparable)) <= 1 else "compatibility_risk"
    return status, has_not_comparable


@dataclass
class CompatibilityEntry:
    service_id: int
    service_name: str
    declared_version: str | None
    major_version: int | None
    effective_version: tuple[int, ...] | None = None


@dataclass
class CompatibilityGroup:
    name: str
    ecosystem: str
    status: str
    has_not_comparable: bool
    entries: list[CompatibilityEntry]


def compute_compatibility(session: Session) -> list[CompatibilityGroup]:
    """FR-001/FR-002: computed fresh from existing Service/Dependency rows —
    no persistence, no separate scan step (research.md §6)."""
    rows = (
        session.query(
            Dependency.name,
            Service.ecosystem,
            Service.id,
            Service.name,
            Dependency.declared_version,
        )
        .join(Service, Dependency.service_id == Service.id)
        .all()
    )

    raw_groups: dict[tuple[str, str], list[tuple[int, str, str | None]]] = defaultdict(list)
    for dep_name, ecosystem, service_id, service_name, declared_version in rows:
        raw_groups[(dep_name, ecosystem)].append((service_id, service_name, declared_version))

    groups: list[CompatibilityGroup] = []
    for (dep_name, ecosystem), raw_entries in raw_groups.items():
        distinct_services = {service_id for service_id, _, _ in raw_entries}
        if len(distinct_services) < 2:
            continue  # FR-001: only dependencies shared by more than one service

        entries = [
            CompatibilityEntry(
                service_id=service_id,
                service_name=service_name,
                declared_version=declared_version,
                major_version=extract_major_version(declared_version),
                effective_version=extract_effective_version(declared_version),
            )
            for service_id, service_name, declared_version in raw_entries
        ]
        status, has_not_comparable = status_for_majors([e.effective_version for e in entries])
        groups.append(
            CompatibilityGroup(
                name=dep_name,
                ecosystem=ecosystem,
                status=status,
                has_not_comparable=has_not_comparable,
                entries=entries,
            )
        )

    return groups


@dataclass
class ConflictingEntry:
    service_id: int
    service_name: str
    declared_version: str | None


@dataclass
class CompatibilityRisk:
    name: str
    ecosystem: str
    declared_version: str | None
    conflicting_with: list[ConflictingEntry]


def risks_for_service(groups: list[CompatibilityGroup], service_id: int) -> list[CompatibilityRisk]:
    """002 FR-014: a service's own compatibility risks, reusing the
    already-computed groups rather than re-querying. A service whose own
    version isn't comparable isn't itself flagged as 'at risk'."""
    risks: list[CompatibilityRisk] = []
    for group in groups:
        own = next((e for e in group.entries if e.service_id == service_id), None)
        if own is None or own.effective_version is None:
            continue

        conflicting = [
            ConflictingEntry(
                service_id=e.service_id, service_name=e.service_name, declared_version=e.declared_version
            )
            for e in group.entries
            if e.service_id != service_id
            and e.effective_version is not None
            and e.effective_version != own.effective_version
        ]
        if conflicting:
            risks.append(
                CompatibilityRisk(
                    name=group.name,
                    ecosystem=group.ecosystem,
                    declared_version=own.declared_version,
                    conflicting_with=conflicting,
                )
            )
    return risks
