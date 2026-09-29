from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class ServiceConnection(Base):
    """A connection between two nodes, each either a registered Service or
    an ExternalNode. Exactly one of `from_service`/`from_external_node` is
    set per side; this is enforced by construction in connection_graph.py,
    not a DB constraint (data-model.md)."""

    __tablename__ = "service_connections"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    from_service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=True
    )
    from_external_node_id: Mapped[int | None] = mapped_column(
        ForeignKey("external_nodes.id", ondelete="CASCADE"), index=True, nullable=True
    )
    to_service_id: Mapped[int | None] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), index=True, nullable=True
    )
    to_external_node_id: Mapped[int | None] = mapped_column(
        ForeignKey("external_nodes.id", ondelete="CASCADE"), index=True, nullable=True
    )
    relationship_basis: Mapped[str] = mapped_column(String, nullable=False)
    source_compose_path: Mapped[str] = mapped_column(String, nullable=False)

    from_service = relationship("Service", foreign_keys=[from_service_id])
    from_external_node = relationship("ExternalNode", foreign_keys=[from_external_node_id])
    to_service = relationship("Service", foreign_keys=[to_service_id])
    to_external_node = relationship("ExternalNode", foreign_keys=[to_external_node_id])
