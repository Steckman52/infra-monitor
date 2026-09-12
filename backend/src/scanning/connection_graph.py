from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from src.models.external_node import ExternalNode
from src.models.service import Service
from src.models.service_connection import ServiceConnection
from src.scanning.parsers.docker_compose import ParsedCompose


@dataclass
class GraphBuildResult:
    external_nodes: list[ExternalNode]
    connections: list[ServiceConnection]


def _node_ref(local_name, resolved_service, external_nodes):
    if local_name in resolved_service:
        return ("service", resolved_service[local_name])
    if local_name in external_nodes:
        return ("external", external_nodes[local_name])
    return None


def _assign_side(connection: ServiceConnection, side: str, ref) -> None:
    kind, obj = ref
    if kind == "service":
        setattr(connection, f"{side}_service", obj)
    else:
        setattr(connection, f"{side}_external_node", obj)


def build_graph_for_compose(
    parsed: ParsedCompose,
    compose_path: Path,
    repository_path: str,
    services_by_build_context: dict[Path, Service],
) -> GraphBuildResult:
    """FR-009/FR-010/FR-011: match each compose service block to a
    registered Service by its resolved build-context path, create an
    ExternalNode for every unmatched block, then derive one connection per
    pair sharing a network and/or a depends_on relationship (never two rows
    for the same pair)."""
    resolved_service: dict[str, Service] = {}
    external_nodes: dict[str, ExternalNode] = {}
    networks_by_name: dict[str, set[str]] = {}
    depends_on_by_name: dict[str, set[str]] = {}

    for block in parsed.services:
        match = (
            services_by_build_context.get(block.build_context)
            if block.build_context is not None
            else None
        )
        if match is not None:
            resolved_service[block.name] = match
        else:
            external_nodes[block.name] = ExternalNode(
                name=block.name,
                image=block.image,
                source_compose_path=str(compose_path),
                repository_path=repository_path,
            )
        networks_by_name[block.name] = set(block.networks)
        depends_on_by_name[block.name] = set(block.depends_on)

    pair_basis: dict[frozenset, set[str]] = defaultdict(set)
    names = list(networks_by_name.keys())
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            if networks_by_name[a] & networks_by_name[b]:
                pair_basis[frozenset((a, b))].add("shared_network")

    for a, deps in depends_on_by_name.items():
        for b in deps:
            if b == a or b not in networks_by_name:
                continue  # ignore self-reference or a name not defined in this file
            pair_basis[frozenset((a, b))].add("depends_on")

    connections: list[ServiceConnection] = []
    for pair, bases in pair_basis.items():
        a, b = tuple(pair)
        ref_a = _node_ref(a, resolved_service, external_nodes)
        ref_b = _node_ref(b, resolved_service, external_nodes)
        if ref_a is None or ref_b is None:
            continue
        basis = "both" if len(bases) == 2 else next(iter(bases))
        connection = ServiceConnection(relationship_basis=basis, source_compose_path=str(compose_path))
        _assign_side(connection, "from", ref_a)
        _assign_side(connection, "to", ref_b)
        connections.append(connection)

    return GraphBuildResult(external_nodes=list(external_nodes.values()), connections=connections)
