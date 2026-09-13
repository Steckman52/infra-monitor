from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, Session, mapped_column

from src.db import Base

SCAN_TYPES = {"registry", "log"}


class ScanMetadata(Base):
    """When each independently-triggered scan type last ran, so the UI can
    show whether registry/log data might be stale. One row per scan_type,
    updated in place -- unlike the data a scan produces, this fact is never
    replaced wholesale, only advanced to the latest run's timestamp."""

    __tablename__ = "scan_metadata"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    scan_type: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)


def record_scan(session: Session, scan_type: str, timestamp: datetime) -> None:
    """Upsert this scan type's last-run timestamp, in the caller's existing
    transaction -- called from within run_scan/run_log_scan themselves, not
    replaced-and-repopulated like the data those scans produce."""
    existing = session.query(ScanMetadata).filter_by(scan_type=scan_type).one_or_none()
    if existing is not None:
        existing.last_run_at = timestamp
    else:
        session.add(ScanMetadata(scan_type=scan_type, last_run_at=timestamp))
