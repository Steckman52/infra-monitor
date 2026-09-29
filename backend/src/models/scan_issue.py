from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base

ISSUE_TYPES = {"unparsable", "incomplete_data", "unreachable_path", "scan_truncated"}


class ScanIssue(Base):
    """A manifest that failed to parse, was incomplete, or a root that was unreachable.

    See data-model.md. `manifest_path` holds the requested root path itself when
    `issue_type == "unreachable_path"`, since no manifest was ever reached.
    """

    __tablename__ = "scan_issues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    manifest_path: Mapped[str] = mapped_column(String, nullable=False)
    repository_path: Mapped[str] = mapped_column(String, nullable=False)
    issue_type: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=True
    )
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    service = relationship("Service", back_populates="scan_issues")
