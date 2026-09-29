from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base

ADR_RELATIONSHIP_TYPES = {"supersedes", "amends"}


class AdrRelationship(Base):
    """A directed supersedes/amends link between two ADRs, normalized to a
    canonical direction (data-model.md) so both 'supersedes' and
    'superseded by' phrasing produce the same row."""

    __tablename__ = "adr_relationships"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    from_adr_id: Mapped[int] = mapped_column(
        ForeignKey("adr_records.id", ondelete="CASCADE"), index=True, nullable=False
    )
    to_adr_id: Mapped[int] = mapped_column(
        ForeignKey("adr_records.id", ondelete="CASCADE"), index=True, nullable=False
    )
    relationship_type: Mapped[str] = mapped_column(String, nullable=False)

    from_adr = relationship("AdrRecord", foreign_keys=[from_adr_id])
    to_adr = relationship("AdrRecord", foreign_keys=[to_adr_id])
