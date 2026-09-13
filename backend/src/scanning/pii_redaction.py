import re

# Constitution Principle III (No Personal Data) names emails as a prohibited
# example. IP addresses are deliberately NOT redacted here (see
# docs/adr/0011-*.md): infrastructure logs' IPs are overwhelmingly
# service/network identifiers, not personal data, and blanket redaction
# would gut the log analysis feature's diagnostic value.
_EMAIL_RE = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")


def redact_pii(text: str) -> str:
    """Replace email addresses in `text` with a fixed placeholder before it
    is persisted or displayed (log_scan_service.py). A small, fixed,
    regex-based heuristic, consistent with the ADR module's own
    secret-pattern approach -- not an exhaustive PII scanner."""
    return _EMAIL_RE.sub("[REDACTED_EMAIL]", text)
