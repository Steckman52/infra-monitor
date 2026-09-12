from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from src.db import Base


class ExternalNode(Base):
    """A docker-compose.yml service block with no matching registered Service
    (e.g. `image:` only, no local build). Scoped per source repository so an
    identically-named node in a different repository stays distinct
    (spec Assumptions)."""

    __tablename__ = "external_nodes"
    __table_args__ = (UniqueConstraint("name", "source_compose_path"),)

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    image: Mapped[str | None] = mapped_column(String, nullable=True)
    source_compose_path: Mapped[str] = mapped_column(String, nullable=False)
    repository_path: Mapped[str] = mapped_column(String, nullable=False)
