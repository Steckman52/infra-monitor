import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

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

_CONTINUATION_PREFIXES = ("at ", "File ", "Caused by:", "... ")

# Levels that mean "this line is an error", mapped to the canonical marker
# stored on the group. Abbreviations matter: nginx and haproxy write `ERR`,
# Kubernetes components write `E`, telegraf writes `E!`.
_ERROR_LEVELS = {
    "ERROR": "ERROR",
    "ERR": "ERROR",
    "E": "ERROR",
    "FATAL": "FATAL",
    "F": "FATAL",
    "EMERG": "FATAL",
    "EMERGENCY": "FATAL",
    "PANIC": "PANIC:",
    "CRIT": "CRITICAL",
    "CRITICAL": "CRITICAL",
    "ALERT": "CRITICAL",
    "SEVERE": "SEVERE",
}

# Levels that mean "this line is NOT an error", however alarming its text.
# This set is the whole reason the false-positive rate drops: a line saying
# `INFO Registered global exception handler` declares its own level, and
# that declaration outranks any scary word in the message.
_NON_ERROR_LEVELS = {
    "TRACE", "DEBUG", "INFO", "INFORMATION", "NOTICE", "WARN", "WARNING",
    "D", "I", "W", "V", "NOTSET", "OK", "SUCCESS",
}

_ALL_LEVELS = set(_ERROR_LEVELS) | _NON_ERROR_LEVELS

# How many leading tokens may be inspected while looking for a level field.
# Enough to step over a timestamp, a pid and a thread name; small enough
# that a level word deep in prose is never mistaken for the level.
_LEVEL_SCAN_TOKENS = 6

# klog (`E0101 12:00:00.000000  1 file.go:10]`) and telegraf (`E!`) put the
# level in the first character of the first token.
_SINGLE_LETTER_LEVEL_RE = re.compile(r"^([EFIWD])[!0-9]")

# logfmt: `level=error`, `lvl=err`, `severity="critical"`. The word boundary
# keeps `log_level=error` from being read as the line's own level.
_LOGFMT_LEVEL_RE = re.compile(r"(?:^|\s)(?:level|lvl|severity)=[\"']?([A-Za-z]+)", re.IGNORECASE)

# A bare exception class opening a line: `java.lang.NullPointerException: …`,
# `ValueError: bad input`. Common as the informative line of a stack trace.
_EXCEPTION_CLASS_RE = re.compile(r"^[\w.$]*(?:Exception|Error)\b\s*:")

_JSON_LEVEL_KEYS = ("level", "severity", "lvl", "loglevel", "log_level")
_JSON_MESSAGE_KEYS = ("msg", "message", "event", "text", "log")
_JSON_TIME_KEYS = ("ts", "time", "timestamp", "@timestamp", "eventTime", "asctime")

# Word-boundary matching, not bare substring: "TypeError"/"ValueError" must
# NOT match the "ERROR" marker, or a "Caused by: TypeError: ..." line inside
# a stack trace would be mistaken for the start of a brand-new error.
_MARKER_PATTERN = re.compile(
    r"\b(" + "|".join(re.escape(m.rstrip(":")) for m in SEVERITY_MARKERS) + r")\b",
    re.IGNORECASE,
)
_MARKER_BY_UPPER_STEM = {marker.rstrip(":").upper(): marker for marker in SEVERITY_MARKERS}

_TIMESTAMP_PATTERNS = [
    # ISO-8601, optionally with fractional seconds and an offset. The offset
    # is captured deliberately: dropping it silently shifted every timestamp
    # from a non-UTC container, so two services logging the same instant
    # appeared hours apart.
    re.compile(r"\d{4}-\d{2}-\d{2}[T ]\d{2}:\d{2}:\d{2}(?:[.,]\d+)?(?:Z|[+-]\d{2}:?\d{2})?"),
]

_ISO_CLEAN_RE = re.compile(r"[.,](\d+)")


@dataclass
class RawErrorEntry:
    first_line: str
    continuation_lines: list[str] = field(default_factory=list)
    start_line_number: int = 0
    severity_marker: str = ""
    # The semantic message, used to build the grouping template. For a plain
    # log line this is the line itself; for a JSON line it is the `msg`
    # field, because templating the whole JSON object collapses every entry
    # in the file into one meaningless group.
    message: str = ""
    # Timestamp lifted out of a structured line, where it is not at column 0.
    structured_timestamp: str | None = None

    def __post_init__(self) -> None:
        if not self.message:
            self.message = self.first_line

    @property
    def raw_text(self) -> str:
        return "\n".join([self.first_line, *self.continuation_lines])


def _parse_json_line(line: str) -> dict | None:
    """One JSON object per line -- what zerolog, zap, pino, winston, bunyan
    and the Python json formatters all emit, and the dominant format in
    modern services."""
    stripped = line.strip()
    if not (stripped.startswith("{") and stripped.endswith("}")):
        return None
    try:
        parsed = json.loads(stripped)
    except (ValueError, RecursionError):
        return None
    return parsed if isinstance(parsed, dict) else None


def _first_key(payload: dict, keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = payload.get(key)
        if isinstance(value, str) and value:
            return value
        if value is not None and not isinstance(value, (dict, list)):
            return str(value)
    return None


def _declared_level(line: str) -> str | None:
    """The level this line declares about itself, upper-cased, or None if it
    declares none. Returning a level -- error or not -- is authoritative."""
    match = _LOGFMT_LEVEL_RE.search(line)
    if match:
        return match.group(1).upper()

    match = _SINGLE_LETTER_LEVEL_RE.match(line.lstrip())
    if match:
        return match.group(1).upper()

    for token in line.split()[:_LEVEL_SCAN_TOKENS]:
        word = token.strip("[](){}<>:,;|-\"'").upper()
        if word in _ALL_LEVELS:
            return word
    return None


def _marker_anywhere(line: str) -> str | None:
    match = _MARKER_PATTERN.search(line)
    if not match:
        return None
    return _MARKER_BY_UPPER_STEM[match.group(1).upper()]


def _severity_of(line: str) -> tuple[str, str, str | None] | None:
    """`(marker, message, timestamp)` when this line starts an error, else None.

    A line that declares its own level is judged by that level and nothing
    else. Only a line with no level field at all falls back to searching for
    a marker anywhere in the text -- which is what used to report
    `INFO Registered global exception handler` as an EXCEPTION.
    """
    payload = _parse_json_line(line)
    if payload is not None:
        level = (_first_key(payload, _JSON_LEVEL_KEYS) or "").upper()
        message = _first_key(payload, _JSON_MESSAGE_KEYS) or line
        timestamp = _first_key(payload, _JSON_TIME_KEYS)
        marker = _ERROR_LEVELS.get(level)
        return (marker, message, timestamp) if marker else None

    level = _declared_level(line)
    if level is not None:
        marker = _ERROR_LEVELS.get(level)
        return (marker, line, None) if marker else None

    if _EXCEPTION_CLASS_RE.match(line.strip()):
        return ("ERROR", line, None)

    marker = _marker_anywhere(line)
    return (marker, line, None) if marker else None


def _starts_new_record(line: str) -> bool:
    """Whether this line begins a new log record rather than continuing one.

    An indented line never does -- a stack frame is indented no matter what
    it contains. An unindented line does if it declares a level or is a JSON
    object, which is what every logger emits at the start of a record.
    """
    if line[:1].isspace():
        return False
    if _parse_json_line(line) is not None:
        return True
    return _declared_level(line) is not None


def _is_continuation(line: str) -> bool:
    if not line.strip():
        return False
    if line[:1] in (" ", "\t"):
        return True
    stripped = line.lstrip()
    if stripped.startswith(_CONTINUATION_PREFIXES):
        return True
    # The unindented exception-class line that logback and the Python logging
    # module print directly under their own message. Treating it as a break
    # dropped the entire stack trace that followed it.
    return bool(_EXCEPTION_CLASS_RE.match(stripped))


def detect_errors(lines: list[str]) -> list[RawErrorEntry]:
    """FR-005/FR-006: scan physical lines for an error-level line, capturing
    immediately-following continuation lines (indented, stack frames, or the
    exception-class line) into the same entry. Capture stops at a blank line,
    a new error line, a non-continuation line, or the fixed max line cap."""
    entries: list[RawErrorEntry] = []
    i = 0
    n = len(lines)
    while i < n:
        detected = _severity_of(lines[i])
        if detected is None:
            i += 1
            continue
        marker, message, structured_timestamp = detected

        start_line_number = i + 1
        continuation: list[str] = []
        j = i + 1
        while j < n and len(continuation) < MAX_CONTINUATION_LINES:
            candidate = lines[j]
            if not _is_continuation(candidate):
                break
            # Only a genuinely new log *record* ends this entry. A record
            # announces itself with a level field or as a JSON object; the
            # exception-class line under a stack trace does not, and
            # treating it as a new error split one incident in two while
            # discarding the frames that followed.
            if _starts_new_record(candidate):
                break
            continuation.append(candidate)
            j += 1

        entries.append(
            RawErrorEntry(
                first_line=lines[i],
                continuation_lines=continuation,
                start_line_number=start_line_number,
                severity_marker=marker,
                message=message,
                structured_timestamp=structured_timestamp,
            )
        )
        i = max(j, i + 1)

    return entries


def _parse_iso(text: str) -> datetime | None:
    candidate = text.strip().replace("Z", "+00:00")
    # `datetime.fromisoformat` accepts a space separator and an offset, and
    # keeps the offset -- unlike the fixed-width strptime this replaced,
    # which truncated `+02:00` and shifted the result by two hours.
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError:
        return None
    # Stored in a naive DateTime column that the frontend renders as UTC, so
    # convert to UTC rather than to local time -- converting to local here
    # would have the frontend apply the offset a second time.
    if parsed.tzinfo is not None:
        parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
    return parsed


def extract_timestamp(line: str, structured: str | None = None) -> datetime | None:
    """FR-009: the timestamp of an error line. `structured` is the value
    lifted out of a JSON/logfmt field, which is not at column 0 and so was
    previously never found. No fabricated result when nothing parses."""
    if structured:
        parsed = _parse_iso(structured)
        if parsed is not None:
            return parsed
        if structured.isdigit():
            # Epoch seconds or milliseconds, as emitted by zerolog and pino.
            value = int(structured)
            try:
                return datetime.fromtimestamp(value / 1000 if value > 10**11 else value)
            except (OverflowError, OSError, ValueError):
                return None

    # Not anchored to column 0 any more: bracketed and syslog-prefixed lines
    # put the timestamp a few characters in.
    match = _TIMESTAMP_PATTERNS[0].search(line)
    if match:
        return _parse_iso(match.group(0))
    return None
