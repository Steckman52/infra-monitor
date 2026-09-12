from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class AdrImportIssue(Base):
    """A file that failed to parse as an ADR (distinct from
    AdrRecord.has_secret_warning, which applies to a successfully-imported
    record). See data-model.md."""

    __tablename__ = "adr_import_issues"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    path: Mapped[str] = mapped_column(String, nullable=False)
    reason: Mapped[str] = mapped_column(String, nullable=False)
    detected_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
