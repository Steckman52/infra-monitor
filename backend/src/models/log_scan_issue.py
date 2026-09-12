from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base

LOG_SCAN_ISSUE_TYPES = {"unattributed", "unreadable"}


class LogScanIssue(Base):
    """An unattributed log directory or an unreadable log file. Kept in its
    own table, separate from the registry's ScanIssue (research.md §3),
    so the two independently-triggered scans never clobber each other's
    issue records."""

    __tablename__ = "log_scan_issues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String, nullable=False)
    issue_type: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
