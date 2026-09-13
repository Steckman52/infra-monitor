import re

# research.md §8: three fixed, documented patterns -- a heuristic warning,
# never a blocker (Constitution Principle VIII / FR-007).
_PRIVATE_KEY_RE = re.compile(r"-----BEGIN (RSA |EC |)PRIVATE KEY-----")
_AWS_ACCESS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")
_GENERIC_CREDENTIAL_RE = re.compile(
    r"(?i)\b(password|passwd|secret|token|api[_-]?key)\b\s*[:=]\s*['\"]?[A-Za-z0-9\-_/+=]{8,}"
)


def check_for_secrets(content: str) -> bool:
    return bool(
        _PRIVATE_KEY_RE.search(content)
        or _AWS_ACCESS_KEY_RE.search(content)
        or _GENERIC_CREDENTIAL_RE.search(content)
    )


def describe_secret_warning(content: str) -> str | None:
    """Human-readable reason for the first research.md §8 pattern that
    matches `content`, for the combined issues/warnings view (FR-011).
    Returns None when none match."""
    if _PRIVATE_KEY_RE.search(content):
        return "Content resembles a private key"
    if _AWS_ACCESS_KEY_RE.search(content):
        return "Content resembles an AWS access key"
    if _GENERIC_CREDENTIAL_RE.search(content):
        return "Content resembles a generic credential assignment"
    return None
