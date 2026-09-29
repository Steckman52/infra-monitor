import importlib

import pytest

from src import config


def _reload(monkeypatch, **env):
    for key, value in env.items():
        monkeypatch.setenv(f"INFRA_MONITOR_{key}", value)
    return importlib.reload(config)


@pytest.fixture(autouse=True)
def _restore_defaults():
    yield
    importlib.reload(config)


def test_defaults_need_no_configuration(monkeypatch):
    for key in ("DB_PATH", "MAX_DIRECTORIES", "MAX_LOG_FILE_MB", "EXCLUDED_DIRS", "ALLOWED_HOSTS"):
        monkeypatch.delenv(f"INFRA_MONITOR_{key}", raising=False)
    cfg = importlib.reload(config)

    assert cfg.MAX_DIRECTORIES_WALKED == 50_000
    assert cfg.MAX_LOG_FILE_MB == 200
    assert cfg.EXTRA_EXCLUDED_DIRS == []
    assert cfg.DB_PATH.name == "registry.db"


def test_values_are_read_from_the_environment(monkeypatch, tmp_path):
    cfg = _reload(
        monkeypatch,
        DB_PATH=str(tmp_path / "custom.db"),
        MAX_DIRECTORIES="200000",
        EXCLUDED_DIRS=".gradle, Pods ,build",
    )

    assert cfg.DB_PATH == tmp_path / "custom.db"
    assert cfg.MAX_DIRECTORIES_WALKED == 200_000
    assert cfg.EXTRA_EXCLUDED_DIRS == [".gradle", "Pods", "build"]


@pytest.mark.parametrize("bad", ["lots", "0", "-5"])
def test_a_malformed_number_fails_loudly_at_startup(monkeypatch, bad):
    # A typo in a limit must stop the tool with a message, not silently fall
    # back to a default the operator did not ask for.
    with pytest.raises(ValueError, match="INFRA_MONITOR_MAX_DIRECTORIES"):
        _reload(monkeypatch, MAX_DIRECTORIES=bad)
