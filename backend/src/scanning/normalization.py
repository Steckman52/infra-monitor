import re

_UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_HEX_PREFIXED_RE = re.compile(r"0x[0-9a-fA-F]+")

# Bare hex runs: request ids, trace/span ids, git SHAs, container ids. These
# were the single biggest source of false distinctions -- a bare-digit
# substitution shredded `d41d8cd98f00b204` into `d<NUM>d<NUM>cd<NUM>...`, so
# the same error with a different request id became a different group and
# occurrence_count never rose above 1. Seven is long enough to clear ordinary
# words and short version numbers.
_HEX_RUN_RE = re.compile(r"\b[0-9a-f]{7,}\b", re.IGNORECASE)

# Kubernetes pod/replicaset suffixes: `api-7d9f8b6c4-x2k9p`. The random
# suffix differs per pod, so without this every pod reports its own group.
_POD_SUFFIX_RE = re.compile(r"\b([a-z0-9][a-z0-9-]*?)-[a-z0-9]{8,10}-[a-z0-9]{5}\b")

# Filesystem paths and URLs, whose variable segment (tenant, date, host) is
# rarely what distinguishes two errors.
_PATH_RE = re.compile(r"(?:[A-Za-z]:)?(?:/|\\\\)[\w.\-/\\\\]{2,}")
_URL_RE = re.compile(r"\b[a-z][a-z0-9+.-]*://[^\s\"']+", re.IGNORECASE)

# Quoted runs are NOT collapsed wholesale any more. In most real loggers the
# message itself is the quoted part (`msg="connection refused"`), so erasing
# it merged genuinely different failures into one row. Only quoted runs that
# look like *data* rather than prose are collapsed: long, or containing a
# digit, or with no spaces at all.
_QUOTED_RE = re.compile(r'"([^"]*)"|\'([^\']*)\'')

_DIGITS_RE = re.compile(r"\d+")


def _looks_like_data(value: str) -> bool:
    """A quoted run worth replacing: an identifier, path or value, not a
    human-readable phrase that distinguishes this error from another."""
    if len(value) > 40:
        return True
    if any(ch.isdigit() for ch in value):
        return True
    return " " not in value.strip() and len(value) > 12


def _replace_quoted(match: re.Match) -> str:
    value = match.group(1) if match.group(1) is not None else match.group(2)
    quote = '"' if match.group(1) is not None else "'"
    if _looks_like_data(value):
        return f"{quote}<STR>{quote}"
    return match.group(0)


def normalize_template(message: str) -> str:
    """FR-007: substitute most-specific-first (research.md §5) so a UUID,
    hex id or path isn't fragmented by a premature bare-digit substitution.

    The goal is that two occurrences of *the same* failure produce the same
    template while two *different* failures do not -- occurrence_count is
    only meaningful if both halves hold.
    """
    text = _URL_RE.sub("<URL>", message)
    text = _UUID_RE.sub("<UUID>", text)
    text = _HEX_PREFIXED_RE.sub("<HEX>", text)
    text = _POD_SUFFIX_RE.sub(r"\1-<POD>", text)
    text = _PATH_RE.sub("<PATH>", text)
    text = _HEX_RUN_RE.sub("<HEX>", text)
    text = _QUOTED_RE.sub(_replace_quoted, text)
    text = _DIGITS_RE.sub("<NUM>", text)
    return text
