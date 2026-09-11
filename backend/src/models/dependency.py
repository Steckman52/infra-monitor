from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db import Base


class Dependency(Base):
    """A single direct dependency declared by a service's manifest. See data-model.md."""

    __tablename__ = "dependencies"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    service_id: Mapped[int] = mapped_column(
        ForeignKey("services.id", ondelete="CASCADE"), nullable=False
    )
    name: Mapped[str] = mapped_column(String, nullable=False)
    declared_version: Mapped[str | None] = mapped_column(String, nullable=True)

    service = relationship("Service", back_populates="dependencies")
