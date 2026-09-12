import re
from dataclasses import dataclass, field
from datetime import datetime

SEVERITY_MARKERS = [
    "ERROR",
    "FATAL",
    "SEVERE",
    "CRITICAL",
    "EXCEPTION",
    "TRACEBACK",
    "PANIC:",
    "UNHANDLED",
]

MAX_CONTINUATION_LINES = 200

_CONTINUATION_PREFIXES = ("at ", "File ", "Caused by:")

_TIMESTAMP_FORMATS = [
    (re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}"), "%Y-%m-%dT%H:%M:%S"),
    (re.compile(r"^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}"), "%Y-%m-%d %H:%M:%S"),
]

# Word-boundary matching, not bare substring: "TypeError"/"ValueError" must
# NOT match the "ERROR" marker, or a "Caused by: TypeError: ..." line inside
# a stack trace would be mistaken for the start of a brand-new error.
_MARKER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(m.rstrip(":")) for m in SEVERITY_MARKERS) + r")\b",
    re.IGNORECASE,
)
_MARKER_BY_UPPER_STEM = {marker.rstrip(":").upper(): marker for marker in SEVERITY_MARKERS}


@dataclass
class RawErrorEntry:
    first_line: str
    continuation_lines: list[str] = field(default_factory=list)
    start_line_number: int = 0
    severity_marker: str = ""

    @property
    def raw_text(self) -> str:
        return "\n".join([self.first_line, *self.continuation_lines])


def _matching_marker(line: str) -> str | None:
    match = _MARKER_PATTERN.search(line)
    if not match:
        return None
    return _MARKER_BY_UPPER_STEM[match.group(1).upper()]


def _is_continuation(line: str) -> bool:
    if not line.strip():
        return False
    if line[:1] in (" ", "\t"):
        return True
    return line.lstrip().startswith(_CONTINUATION_PREFIXES)


def detect_errors(lines: list[str]) -> list[RawErrorEntry]:
    """FR-005/FR-006: scan physical lines for a severity marker, capturing
    immediately-following continuation lines (indented, or starting with
    `at `/`File `/`Caused by:`) into the same entry. Capture stops at a
    blank line, a new marker, a non-continuation line, or the fixed max
    line cap — whichever comes first."""
    entries: list[RawErrorEntry] = []
    i = 0
    n = len(lines)
    while i < n:
        marker = _matching_marker(lines[i])
        if marker is None:
            i += 1
            continue

        start_line_number = i + 1
        continuation: list[str] = []
        j = i + 1
        while j < n and len(continuation) < MAX_CONTINUATION_LINES:
            candidate = lines[j]
            if _matching_marker(candidate) is not None:
                break
            if not _is_continuation(candidate):
                break
            continuation.append(candidate)
            j += 1

        entries.append(
            RawErrorEntry(
                first_line=lines[i],
                continuation_lines=continuation,
                start_line_number=start_line_number,
                severity_marker=marker,
            )
        )
        i = j

    return entries


def extract_timestamp(line: str) -> datetime | None:
    """FR-009: try a small, fixed, ordered list of common timestamp prefixes.
    First match wins; no fabricated result when nothing matches."""
    for pattern, fmt in _TIMESTAMP_FORMATS:
        match = pattern.match(line)
        if match:
            try:
                return datetime.strptime(match.group(0), fmt)
            except ValueError:
                continue
    return None
