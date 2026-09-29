from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.db import Base

SCAN_TYPES = {"registry", "log"}


class ScanMetadata(Base):
    """When each independently-triggered scan type last ran, and over which
    roots, so the UI can show whether registry/log data might be stale and
    can offer the previous roots back. One row per scan_type, updated in
    place -- unlike the data a scan produces, this fact is never replaced
    wholesale, only advanced to the latest run."""

    __tablename__ = "scan_metadata"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_type: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    # Newline-separated. Until this existed the roots lived only in React
    # state and were lost on refresh, so a user who had just scanned six
    # repositories had to remember all six paths by hand.
    last_roots: Mapped[str | None] = mapped_column(String, nullable=True)


def record_scan(
    session: Session, scan_type: str, timestamp: datetime, roots: list[str] | None = None
) -> None:
    """Upsert this scan type's last-run timestamp and roots, in the caller's
    existing transaction -- called from within run_scan/run_log_scan
    themselves, not replaced-and-repopulated like the data those scans
    produce."""
    serialized = "\n".join(roots) if roots else None
    existing = session.query(ScanMetadata).filter_by(scan_type=scan_type).one_or_none()
    if existing is not None:
        existing.last_run_at = timestamp
        if serialized is not None:
            existing.last_roots = serialized
    else:
        session.add(
            ScanMetadata(scan_type=scan_type, last_run_at=timestamp, last_roots=serialized)
        )
