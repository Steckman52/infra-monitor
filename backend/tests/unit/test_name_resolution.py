from pathlib import Path

from src.scanning import name_resolution


def test_explicit_name_takes_priority():
    name = name_resolution.resolve_name(
        "payments-api", Path("/repos/x/package.json"), set()
    )
    assert name == "payments-api"


def test_falls_back_to_parent_directory_name():
    name = name_resolution.resolve_name(
        None, Path("/repos/inventory-service/requirements.txt"), set()
    )
    assert name == "inventory-service"


def test_collision_appends_suffix():
    existing = {"service"}
    name = name_resolution.resolve_name(
        None, Path("/repos/repo-b/service/package.json"), existing
    )
    assert name != "service"
    assert name.startswith("service")
    assert name not in existing


def test_non_string_explicit_name_falls_back_to_directory_name():
    # A manifest's "name" field is arbitrary JSON -- a number or object would
    # otherwise reach the DB layer and fail as a SQLite bind-parameter error.
    name = name_resolution.resolve_name(
        12345, Path("/repos/inventory-service/package.json"), set()
    )
    assert name == "inventory-service"
