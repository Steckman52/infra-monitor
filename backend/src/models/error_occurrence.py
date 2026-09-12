from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class ErrorOccurrence(Base):
    """A bounded sample (up to 20 per group, research.md §7) of individual
    captured error instances."""

    __tablename__ = "error_occurrences"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    error_group_id: Mapped[int] = mapped_column(
        ForeignKey("error_groups.id", ondelete="CASCADE"), nullable=False
    )
    raw_text: Mapped[str] = mapped_column(String, nullable=False)
    occurred_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    source_log_path: Mapped[str] = mapped_column(String, nullable=False)
    line_number: Mapped[int] = mapped_column(Integer, nullable=False)

    error_group = relationship("ErrorGroup", back_populates="occurrences")
