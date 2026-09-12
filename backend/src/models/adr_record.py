from datetime import date

from sqlalchemy import Boolean, Date, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class AdrRecord(Base):
    """One imported ADR file. See data-model.md."""

    __tablename__ = "adr_records"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    raw_status: Mapped[str | None] = mapped_column(String, nullable=True)
    normalized_status: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[date | None] = mapped_column(Date, nullable=True)
    source_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    repository_path: Mapped[str] = mapped_column(String, nullable=False)
    content: Mapped[str] = mapped_column(String, nullable=False)
    has_secret_warning: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
