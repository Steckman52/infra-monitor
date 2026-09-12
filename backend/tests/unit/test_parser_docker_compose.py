import pytest

from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import docker_compose


def test_build_as_string_and_mapping_resolve_same_context(tmp_path):
    (tmp_path / "svc").mkdir()

    compose1 = tmp_path / "docker-compose.yml"
    compose1.write_text("services:\n  api:\n    build: ./svc\n", encoding="utf-8")
    result1 = docker_compose.parse(compose1)

    compose2 = tmp_path / "docker-compose2.yml"
    compose2.write_text(
        "services:\n  api:\n    build:\n      context: ./svc\n", encoding="utf-8"
    )
    result2 = docker_compose.parse(compose2)

    expected = (tmp_path / "svc").resolve()
    assert result1.services[0].build_context == expected
    assert result2.services[0].build_context == expected


def test_networks_list_and_mapping_normalize_the_same(tmp_path):
    compose1 = tmp_path / "a.yml"
    compose1.write_text(
        "services:\n  api:\n    networks:\n      - net1\n      - net2\n", encoding="utf-8"
    )
    compose2 = tmp_path / "b.yml"
    compose2.write_text(
        "services:\n  api:\n    networks:\n      net1:\n        aliases: [x]\n      net2: {}\n",
        encoding="utf-8",
    )

    r1 = docker_compose.parse(compose1)
    r2 = docker_compose.parse(compose2)

    assert set(r1.services[0].networks) == {"net1", "net2"}
    assert set(r2.services[0].networks) == {"net1", "net2"}


def test_depends_on_list_and_mapping_normalize_the_same(tmp_path):
    compose1 = tmp_path / "a.yml"
    compose1.write_text(
        "services:\n  api:\n    depends_on:\n      - db\n      - cache\n", encoding="utf-8"
    )
    compose2 = tmp_path / "b.yml"
    compose2.write_text(
        "services:\n  api:\n    depends_on:\n      db:\n        condition: service_started\n      cache: {}\n",
        encoding="utf-8",
    )

    r1 = docker_compose.parse(compose1)
    r2 = docker_compose.parse(compose2)

    assert set(r1.services[0].depends_on) == {"db", "cache"}
    assert set(r2.services[0].depends_on) == {"db", "cache"}


def test_image_only_service_has_no_build_context(tmp_path):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text("services:\n  db:\n    image: postgres:15\n", encoding="utf-8")

    result = docker_compose.parse(compose)

    assert result.services[0].image == "postgres:15"
    assert result.services[0].build_context is None


def test_invalid_yaml_raises_manifest_parse_error(tmp_path):
    compose = tmp_path / "docker-compose.yml"
    compose.write_text("services:\n  api:\n    networks: [unterminated\n", encoding="utf-8")

    with pytest.raises(ManifestParseError):
        docker_compose.parse(compose)
