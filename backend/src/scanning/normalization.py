import re

_UUID_RE = re.compile(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}")
_HEX_RE = re.compile(r"0x[0-9a-fA-F]+")
_QUOTED_RE = re.compile(r'"[^"]*"|\'[^\']*\'')
_DIGITS_RE = re.compile(r"\d+")


def normalize_template(first_line: str) -> str:
    """FR-007: substitute most-specific-first (research.md §5) so a UUID or
    hex address isn't fragmented by a premature bare-digit substitution."""
    text = _UUID_RE.sub("<UUID>", first_line)
    text = _HEX_RE.sub("<HEX>", text)
    text = _QUOTED_RE.sub("<STR>", text)
    text = _DIGITS_RE.sub("<NUM>", text)
    return text
