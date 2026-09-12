from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from sqlalchemy.orm import Session

from src.models.error_group import ErrorGroup
from src.models.error_occurrence import ErrorOccurrence
from src.models.log_scan_issue import LogScanIssue
from src.models.service import Service
from src.scanning.error_detection import detect_errors, extract_timestamp
from src.scanning.normalization import normalize_template
from src.scanning.walker import find_log_files

MAX_STORED_OCCURRENCES_PER_GROUP = 20


@dataclass
class LogScanSummary:
    error_groups_found: int
    issues_found: int


def run_log_scan(session: Session, root: str) -> LogScanSummary:
    """FR-001/FR-015: an independently-triggered scan (separate from the
    registry scan) that replaces error_groups/error_occurrences/
    log_scan_issues in one transaction (research.md §1, §3)."""
    now = datetime.now(timezone.utc)
    root_path = Path(root)
    services_by_name = {service.name: service for service in session.query(Service).all()}

    groups: dict[tuple, dict] = {}
    issues_to_add: list[LogScanIssue] = []
    unattributed_dirs_seen: set[str] = set()

    for log_path in find_log_files(root_path):
        parent_dir_name = log_path.parent.name
        matched_service = services_by_name.get(parent_dir_name)
        unattributed_source_path = None if matched_service else str(log_path.parent)

        if matched_service is None and unattributed_source_path not in unattributed_dirs_seen:
            # FR-004: recorded once per distinct unmatched directory, not
            # silently dropped and not attributed to an arbitrary service.
            unattributed_dirs_seen.add(unattributed_source_path)
            issues_to_add.append(
                LogScanIssue(
                    path=unattributed_source_path,
                    issue_type="unattributed",
                    reason=f"No registered service named '{parent_dir_name}'",
                    detected_at=now,
                )
            )

        try:
            text = log_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as exc:
            # FR-014: isolate this file's failure, keep scanning the rest.
            issues_to_add.append(
                LogScanIssue(path=str(log_path), issue_type="unreadable", reason=str(exc), detected_at=now)
            )
            continue

        service_id = matched_service.id if matched_service else None
        for entry in detect_errors(text.splitlines()):
            template = normalize_template(entry.first_line)
            timestamp = extract_timestamp(entry.first_line)
            key = (service_id, unattributed_source_path, template)

            group = groups.setdefault(
                key,
                {
                    "service_id": service_id,
                    "unattributed_source_path": unattributed_source_path,
                    "normalized_template": template,
                    "severity_marker": entry.severity_marker,
                    "occurrence_count": 0,
                    "first_seen": None,
                    "last_seen": None,
                    "example_text": entry.raw_text,
                    "occurrences": [],
                },
            )
            group["occurrence_count"] += 1
            if timestamp is not None:
                if group["first_seen"] is None or timestamp < group["first_seen"]:
                    group["first_seen"] = timestamp
                if group["last_seen"] is None or timestamp > group["last_seen"]:
                    group["last_seen"] = timestamp
            if len(group["occurrences"]) < MAX_STORED_OCCURRENCES_PER_GROUP:
                # research.md §7: bounded sample; occurrence_count still tracks the true total.
                group["occurrences"].append(
                    {
                        "raw_text": entry.raw_text,
                        "occurred_at": timestamp,
                        "source_log_path": str(log_path),
                        "line_number": entry.start_line_number,
                    }
                )

    error_groups_to_add: list[ErrorGroup] = []
    for group in groups.values():
        group_row = ErrorGroup(
            service_id=group["service_id"],
            unattributed_source_path=group["unattributed_source_path"],
            normalized_template=group["normalized_template"],
            severity_marker=group["severity_marker"],
            occurrence_count=group["occurrence_count"],
            first_seen=group["first_seen"],
            last_seen=group["last_seen"],
            example_text=group["example_text"],
        )
        group_row.occurrences = [
            ErrorOccurrence(
                raw_text=occurrence["raw_text"],
                occurred_at=occurrence["occurred_at"],
                source_log_path=occurrence["source_log_path"],
                line_number=occurrence["line_number"],
            )
            for occurrence in group["occurrences"]
        ]
        error_groups_to_add.append(group_row)

    # Replace all prior log-scan results in one transaction, independent of
    # the registry's own scan/replace transaction (research.md §1).
    session.query(ErrorOccurrence).delete()
    session.query(LogScanIssue).delete()
    session.query(ErrorGroup).delete()
    session.add_all(error_groups_to_add)
    session.add_all(issues_to_add)
    session.commit()

    return LogScanSummary(
        error_groups_found=len(error_groups_to_add),
        issues_found=len(issues_to_add),
    )
