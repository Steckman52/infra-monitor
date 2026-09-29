from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class AdrServiceAssociation(Base):
    """Many-to-many link between an ADR and a registered service
    (data-model.md) — a monorepo's docs/adr relates to every service
    inside it, not one arbitrarily chosen owner."""

    __tablename__ = "adr_service_associations"
    __table_args__ = (UniqueConstraint("adr_id", "service_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    adr_id: Mapped[int] = mapped_column(ForeignKey("adr_records.id", ondelete="CASCADE"), index=True, nullable=False)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=False
    )

    adr = relationship("AdrRecord")
    service = relationship("Service")
