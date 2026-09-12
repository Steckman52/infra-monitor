from datetime import datetime
from pathlib import Path

from src.models.service import Service
from src.scanning.connection_graph import build_graph_for_compose
from src.scanning.parsers.docker_compose import ComposeServiceBlock, ParsedCompose


def _service(**overrides):
    defaults = dict(
        id=1,
        name="api-svc",
        ecosystem="node",
        repository_path="/repo",
        manifest_path="/repo/package.json",
        is_complete=True,
        last_scanned_at=datetime(2026, 1, 1),
    )
    defaults.update(overrides)
    return Service(**defaults)


def test_matching_build_context_resolves_to_registered_service():
    build_context = Path("/repos/api").resolve()
    service = _service(id=1)
    block = ComposeServiceBlock(name="api", build_context=build_context, image=None)
    parsed = ParsedCompose(services=[block])

    result = build_graph_for_compose(
        parsed, Path("/repos/docker-compose.yml"), "/repos", {build_context: service}
    )

    assert result.external_nodes == []
    assert result.connections == []


def test_unmatched_build_context_becomes_external_node():
    block = ComposeServiceBlock(name="db", build_context=None, image="postgres:15")
    parsed = ParsedCompose(services=[block])

    result = build_graph_for_compose(parsed, Path("/repos/docker-compose.yml"), "/repos", {})

    assert len(result.external_nodes) == 1
    assert result.external_nodes[0].name == "db"
    assert result.external_nodes[0].image == "postgres:15"
    assert result.external_nodes[0].repository_path == "/repos"


def test_two_external_nodes_same_name_different_repos_stay_distinct():
    block = ComposeServiceBlock(name="postgres", build_context=None, image="postgres:15")

    result_a = build_graph_for_compose(
        ParsedCompose(services=[block]), Path("/repo-a/docker-compose.yml"), "/repo-a", {}
    )
    result_b = build_graph_for_compose(
        ParsedCompose(services=[block]), Path("/repo-b/docker-compose.yml"), "/repo-b", {}
    )

    node_a = result_a.external_nodes[0]
    node_b = result_b.external_nodes[0]
    assert node_a is not node_b
    assert node_a.repository_path != node_b.repository_path
    assert node_a.source_compose_path != node_b.source_compose_path


def test_shared_network_and_depends_on_collapse_to_a_single_both_connection():
    block_a = ComposeServiceBlock(
        name="api", build_context=None, image="a", networks=["net"], depends_on=["db"]
    )
    block_b = ComposeServiceBlock(name="db", build_context=None, image="postgres", networks=["net"])
    parsed = ParsedCompose(services=[block_a, block_b])

    result = build_graph_for_compose(parsed, Path("/repo/docker-compose.yml"), "/repo", {})

    assert len(result.connections) == 1
    assert result.connections[0].relationship_basis == "both"


def test_shared_network_only_without_depends_on():
    block_a = ComposeServiceBlock(name="api", build_context=None, image="a", networks=["net"])
    block_b = ComposeServiceBlock(name="worker", build_context=None, image="b", networks=["net"])
    parsed = ParsedCompose(services=[block_a, block_b])

    result = build_graph_for_compose(parsed, Path("/repo/docker-compose.yml"), "/repo", {})

    assert len(result.connections) == 1
    assert result.connections[0].relationship_basis == "shared_network"


def test_depends_on_only_without_shared_network():
    block_a = ComposeServiceBlock(name="api", build_context=None, image="a", depends_on=["cache"])
    block_b = ComposeServiceBlock(name="cache", build_context=None, image="redis")
    parsed = ParsedCompose(services=[block_a, block_b])

    result = build_graph_for_compose(parsed, Path("/repo/docker-compose.yml"), "/repo", {})

    assert len(result.connections) == 1
    assert result.connections[0].relationship_basis == "depends_on"
