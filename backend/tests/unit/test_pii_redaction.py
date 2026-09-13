from src.scanning.pii_redaction import redact_pii


def test_email_address_is_redacted():
    result = redact_pii("User john.doe@example.com login failed")
    assert "john.doe@example.com" not in result
    assert "[REDACTED_EMAIL]" in result


def test_multiple_emails_are_all_redacted():
    result = redact_pii("cc: a@example.com, b@example.org")
    assert "a@example.com" not in result
    assert "b@example.org" not in result
    assert result.count("[REDACTED_EMAIL]") == 2


def test_ordinary_text_is_unchanged():
    text = "2026-09-01 03:15:00 ERROR Connection refused: db:5432 attempt 1"
    assert redact_pii(text) == text


def test_ip_addresses_are_left_alone():
    # Deliberate scope decision (see ADR): infra logs' IPs are overwhelmingly
    # service/network identifiers, not personal data, and blanket-redacting
    # them would gut the log analysis feature's diagnostic value.
    text = "Connection refused: 10.0.0.5:5432"
    assert redact_pii(text) == text
