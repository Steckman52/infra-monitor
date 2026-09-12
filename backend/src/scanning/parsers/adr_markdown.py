import re
from dataclasses import dataclass
from datetime import date as date_type
from datetime import datetime
from pathlib import Path

from src.scanning.parsed_manifest import ManifestParseError

_TITLE_RE = re.compile(r"^#\s+(.+)$", re.MULTILINE)
_STATUS_RE = re.compile(r"^\*\s*Status:\s*(.+)$", re.MULTILINE | re.IGNORECASE)
_DATE_RE = re.compile(r"^\*\s*Date:\s*(\d{4}-\d{2}-\d{2})", re.MULTILINE | re.IGNORECASE)

# research.md §4: checked in this order, first match wins.
_STATUS_KEYWORDS = ["superseded", "deprecated", "rejected", "accepted", "proposed"]


@dataclass
class AdrFields:
    title: str
    raw_status: str | None
    normalized_status: str
    date: date_type | None
    content: str


def _normalize_status(raw_status: str | None) -> str:
    if not raw_status:
        return "unrecognized"
    lower = raw_status.lower()
    for keyword in _STATUS_KEYWORDS:
        if keyword in lower:
            return keyword
    return "unrecognized"


def parse(path: Path) -> AdrFields:
    """FR-003/FR-004: extract title/status/date per this project's own MADR
    conventions (research.md §3). A missing title is a parse failure; a
    missing/unrecognized status or date degrades gracefully instead."""
    try:
        content = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError) as exc:
        raise ManifestParseError(f"Cannot read file: {exc}") from exc

    if not content.strip():
        raise ManifestParseError("file is empty")

    title_match = _TITLE_RE.search(content)
    if not title_match:
        raise ManifestParseError("No title heading (# ...) found")
    title = title_match.group(1).strip()

    status_match = _STATUS_RE.search(content)
    raw_status = status_match.group(1).strip() if status_match else None

    parsed_date: date_type | None = None
    date_match = _DATE_RE.search(content)
    if date_match:
        try:
            parsed_date = datetime.strptime(date_match.group(1), "%Y-%m-%d").date()
        except ValueError:
            parsed_date = None

    return AdrFields(
        title=title,
        raw_status=raw_status,
        normalized_status=_normalize_status(raw_status),
        date=parsed_date,
        content=content,
    )
