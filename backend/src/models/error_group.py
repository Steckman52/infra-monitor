from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class ErrorGroup(Base):
    """A distinct recurring error for one service, or for one unattributed
    source directory. See data-model.md for the grouping key rationale."""

    __tablename__ = "error_groups"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=True
    )
    unattributed_source_path: Mapped[str | None] = mapped_column(String, nullable=True)
    normalized_template: Mapped[str] = mapped_column(String, nullable=False)
    severity_marker: Mapped[str] = mapped_column(String, nullable=False)
    occurrence_count: Mapped[int] = mapped_column(Integer, nullable=False)
    first_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_seen: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    example_text: Mapped[str] = mapped_column(String, nullable=False)

    service = relationship("Service")
    occurrences = relationship(
        "ErrorOccurrence", back_populates="error_group", cascade="all, delete-orphan"
    )
