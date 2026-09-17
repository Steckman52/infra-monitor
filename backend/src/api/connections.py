from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.db import get_session
from src.models.external_node import ExternalNode
from src.models.service import Service
from src.models.service_connection import ServiceConnection

router = APIRouter(prefix="/api", tags=["connections"])


class NodeRef(BaseModel):
    type: str
    id: int
    name: str
    repository_path: str | None = None


class ConnectionOut(BaseModel):
    node: NodeRef
    relationship_basis: str


class NodeConnectionsOut(BaseModel):
    node: NodeRef
    connections: list[ConnectionOut]


def _ref(service: Service | None, external_node: ExternalNode | None) -> NodeRef | None:
    if service is not None:
        return NodeRef(type="service", id=service.id, name=service.name)
    if external_node is not None:
        # Two independent repositories can declare a compose service with the
        # same generic name (e.g. "db"); they stay distinct rows (ExternalNode
        # is unique on name + source_compose_path), but without the
        # repository_path the UI has no way to tell them apart.
        return NodeRef(
            type="external",
            id=external_node.id,
            name=external_node.name,
            repository_path=external_node.repository_path,
        )
    return None


def build_adjacency(session: Session) -> dict[tuple[str, int], NodeConnectionsOut]:
    """Shared by GET /api/connections and the service-detail enrichment
    (002 US3) so both read the same symmetric adjacency list."""
    adjacency: dict[tuple[str, int], dict] = {}

    def add_edge(a: NodeRef, b: NodeRef, basis: str) -> None:
        entry = adjacency.setdefault((a.type, a.id), {"node": a, "connections": []})
        entry["connections"].append(ConnectionOut(node=b, relationship_basis=basis))

    for row in session.query(ServiceConnection).all():
        a = _ref(row.from_service, row.from_external_node)
        b = _ref(row.to_service, row.to_external_node)
        if a is None or b is None:
            continue
        add_edge(a, b, row.relationship_basis)
        add_edge(b, a, row.relationship_basis)

    return {
        key: NodeConnectionsOut(node=entry["node"], connections=entry["connections"])
        for key, entry in adjacency.items()
    }


@router.get("/connections", response_model=list[NodeConnectionsOut])
def list_connections(session: Session = Depends(get_session)) -> list[NodeConnectionsOut]:
    return list(build_adjacency(session).values())
