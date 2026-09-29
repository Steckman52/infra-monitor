from datetime import datetime

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.analysis.version_compatibility import compute_compatibility
from src.db import get_session
from src.models.adr_import_issue import AdrImportIssue
from src.models.adr_record import AdrRecord
from src.models.error_group import ErrorGroup
from src.models.log_scan_issue import LogScanIssue
from src.models.scan_issue import ScanIssue
from src.models.scan_metadata import ScanMetadata
from src.models.service import Service

router = APIRouter(prefix="/api", tags=["dashboard"])


class DashboardSummary(BaseModel):
    services_count: int
    scan_issues_count: int
    compatibility_risks_count: int
    error_groups_count: int
    log_scan_issues_count: int
    adrs_count: int
    adr_issues_count: int
    last_registry_scan_at: datetime | None
    last_log_scan_at: datetime | None
    # The roots each scan last ran over, so the UI can offer them back
    # instead of the user having to remember every path by hand.
    last_registry_roots: list[str]
    last_log_roots: list[str]


def _metadata(session: Session, scan_type: str) -> ScanMetadata | None:
    return session.query(ScanMetadata).filter_by(scan_type=scan_type).one_or_none()


def _last_run_at(row: ScanMetadata | None) -> datetime | None:
    return row.last_run_at if row is not None else None


def _last_roots(row: ScanMetadata | None) -> list[str]:
    if row is None or not row.last_roots:
        return []
    return [line for line in row.last_roots.splitlines() if line]


@router.get("/dashboard", response_model=DashboardSummary)
def get_dashboard(session: Session = Depends(get_session)) -> DashboardSummary:
    """Aggregates a count from each of the four features' own data, so the
    landing page can point at whichever screens actually need attention
    without duplicating any of those features' own counting logic."""
    compatibility_risks_count = sum(
        1 for group in compute_compatibility(session) if group.status == "compatibility_risk"
    )
    registry_meta = _metadata(session, "registry")
    log_meta = _metadata(session, "log")
    adr_issues_count = session.query(AdrImportIssue).count() + (
        session.query(AdrRecord).filter(AdrRecord.has_secret_warning.is_(True)).count()
    )

    return DashboardSummary(
        services_count=session.query(Service).count(),
        scan_issues_count=session.query(ScanIssue).count(),
        compatibility_risks_count=compatibility_risks_count,
        error_groups_count=session.query(ErrorGroup).count(),
        log_scan_issues_count=session.query(LogScanIssue).count(),
        adrs_count=session.query(AdrRecord).count(),
        adr_issues_count=adr_issues_count,
        last_registry_scan_at=_last_run_at(registry_meta),
        last_log_scan_at=_last_run_at(log_meta),
        last_registry_roots=_last_roots(registry_meta),
        last_log_roots=_last_roots(log_meta),
    )
