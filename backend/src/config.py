"""Runtime settings, read once from environment variables.

Every value has a default that suits a single user on one machine, so the
tool needs no configuration to run. The variables exist for the cases a
company actually hits: keeping the database somewhere other than the
checkout, scanning a monorepo larger than the default walk cap, or excluding
a vendor directory this tool does not know about (`.gradle`, `Pods`, ...).
"""

import os
from pathlib import Path

_PREFIX = "INFRA_MONITOR_"


def _int(name: str, default: int) -> int:
    raw = os.environ.get(_PREFIX + name)
    if raw is None or not raw.strip():
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ValueError(f"{_PREFIX}{name} must be an integer, got {raw!r}") from exc
    if value <= 0:
        raise ValueError(f"{_PREFIX}{name} must be positive, got {value}")
    return value


def _list(name: str) -> list[str]:
    raw = os.environ.get(_PREFIX + name, "")
    return [item.strip() for item in raw.split(",") if item.strip()]


# Where the SQLite file lives. Everything in it is rebuilt from disk by a
# scan, so moving or deleting it loses nothing but the time to rescan.
DB_PATH = Path(
    os.environ.get(_PREFIX + "DB_PATH")
    or Path(__file__).resolve().parent.parent / "data" / "registry.db"
)

# Upper bound on directories visited per scan root. Hitting it is reported
# as a scan issue, never silently, so raising it is safe.
MAX_DIRECTORIES_WALKED = _int("MAX_DIRECTORIES", 50_000)

# Largest single log file read, in megabytes. Larger files are skipped and
# reported rather than read, since reading is whole-file.
MAX_LOG_FILE_MB = _int("MAX_LOG_FILE_MB", 200)

# Directory names to skip in addition to the built-in list (node_modules,
# vendor, venv, .git, ...). Comma-separated, e.g. ".gradle,Pods,build".
EXTRA_EXCLUDED_DIRS = _list("EXCLUDED_DIRS")

# Hostnames the API answers to, in addition to localhost/127.0.0.1. Only
# needed if the tool is reached through another name; every name added here
# widens who can read what the scans collected.
EXTRA_ALLOWED_HOSTS = _list("ALLOWED_HOSTS")
