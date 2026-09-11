from datetime import datetime

from sqlalchemy import Boolean, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base

ECOSYSTEMS = {"node", "java", "python", "go", "php"}


class Service(Base):
    """One manifest discovered during a scan. See data-model.md."""

    __tablename__ = "services"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    ecosystem: Mapped[str] = mapped_column(String, nullable=False)
    repository_path: Mapped[str] = mapped_column(String, nullable=False)
    manifest_path: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    is_complete: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    last_scanned_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

    dependencies = relationship(
        "Dependency", back_populates="service", cascade="all, delete-orphan"
    )
    scan_issues = relationship(
        "ScanIssue", back_populates="service", cascade="all, delete-orphan"
    )
