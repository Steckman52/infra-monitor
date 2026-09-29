import re

# Constitution Principle III (No Personal Data) names emails as a prohibited
# example. IP addresses are deliberately NOT redacted here (see
# docs/adr/0011-*.md): infrastructure logs' IPs are overwhelmingly
# service/network identifiers, not personal data, and blanket redaction
# would gut the log analysis feature's diagnostic value.
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")

# Credentials are not personal data, so Principle III does not reach them --
# but this tool reads files the user did not write and stores what it finds
# in a database that gets backed up, copied to a colleague, and served over
# an API. An audit demonstrated a root password and an SSH passphrase from a
# log line surviving into the stored template and onto the screen. The
# patterns below are a deliberately small, high-confidence set: each matches
# a credential's *assignment* rather than guessing at bare high-entropy
# strings, so ordinary log text is left intact.
_SECRET_PATTERNS = (
    # key=value / key: value, with the value optionally quoted.
    re.compile(
        r"(?i)\b(password|passwd|pwd|secret|token|api[_-]?key|access[_-]?key|"
        r"auth|authorization|bearer|passphrase|private[_-]?key)\b"
        r"(\s*[:=]\s*)"
        r"(\"[^\"]+\"|'[^']+'|\S+)"
    ),
    # Provider-shaped keys, which are recognisable on their own.
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b"),  # GitHub tokens
    re.compile(r"\bxox[abprs]-[A-Za-z0-9-]{10,}\b"),  # Slack tokens
    # Credentials embedded in a URL: scheme://user:password@host
    re.compile(r"(?i)\b([a-z][a-z0-9+.-]*://[^\s:/@]+:)([^\s@]+)(@)"),
)

# A pasted PEM block is the one case where the secret is the body rather
# than a value after a key. Only the material between the markers is
# replaced: the BEGIN/END lines are what make the record comprehensible
# ("someone pasted a key here"), and the ADR must stay readable -- the
# secret warning is a flag, never a reason to withhold the decision itself.
_PEM_BLOCK_RE = re.compile(
    r"(-----BEGIN [A-Z ]*PRIVATE KEY-----)(.*?)(-----END [A-Z ]*PRIVATE KEY-----)",
    re.DOTALL,
)

_REDACTED = "[REDACTED]"


def _redact_secrets(text: str) -> str:
    text = _PEM_BLOCK_RE.sub(lambda m: f"{m.group(1)}\n{_REDACTED}\n{m.group(3)}", text)
    text = _SECRET_PATTERNS[0].sub(lambda m: f"{m.group(1)}{m.group(2)}{_REDACTED}", text)
    for pattern in _SECRET_PATTERNS[1:-1]:
        text = pattern.sub(_REDACTED, text)
    return _SECRET_PATTERNS[-1].sub(lambda m: f"{m.group(1)}{_REDACTED}{m.group(3)}", text)


def redact_pii(text: str) -> str:
    """Replace email addresses and credential-shaped values in `text` with
    fixed placeholders before it is persisted or displayed. A small, fixed,
    regex-based heuristic, consistent with the ADR module's own
    secret-pattern approach -- not an exhaustive PII or secret scanner.

    The key name is kept and only its value replaced, so the redacted text
    still reads as a log line and still says *what* leaked -- which is the
    part an operator needs in order to go and rotate it.

    Secrets are matched before emails, not after: in a URL like
    `https://user:hunter2@host/path` the email pattern would otherwise claim
    `hunter2@host` first and label a password as an email address.
    """
    return _EMAIL_RE.sub("[REDACTED_EMAIL]", _redact_secrets(text))
