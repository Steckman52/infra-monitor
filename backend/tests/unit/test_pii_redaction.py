import pytest

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


@pytest.mark.parametrize(
    "secret, text",
    [
        ("sup3r-s3cret", "ERROR password: sup3r-s3cret"),
        ("abcd1234efgh5678", 'ERROR api_key = "abcd1234efgh5678"'),
        ("s3cret-token", "ERROR Authorization=s3cret-token rejected"),
        ("AKIAIOSFODNN7EXAMPLE", "ERROR AWS key AKIAIOSFODNN7EXAMPLE rejected"),
        ("ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ012345", "token=ghp_aBcDeFgHiJkLmNoPqRsTuVwXyZ012345"),
        ("hunter2", "ERROR posting to https://svc:hunter2@sentry.io/42"),
    ],
)
def test_credential_values_are_redacted(secret, text):
    # This tool stores what it reads from files the user did not write, in a
    # database that gets backed up and served over an API. A leaked password
    # in a log line must not survive into it.
    result = redact_pii(text)
    assert secret not in result
    assert "[REDACTED]" in result


def test_private_key_material_is_redacted_but_the_record_stays_readable():
    # The ADR module flags a pasted key with has_secret_warning and must
    # still show the decision -- the warning is a flag, never a reason to
    # withhold the record. So redact the body, keep everything else.
    text = (
        "We pasted a key by mistake.\n"
        "-----BEGIN RSA PRIVATE KEY-----\n"
        "MIIEowIBAAKCAQEAfakekeymaterial\n"
        "-----END RSA PRIVATE KEY-----\n"
        "Rotate it."
    )

    result = redact_pii(text)

    assert "MIIEowIBAAKCAQEAfakekeymaterial" not in result
    assert "-----BEGIN RSA PRIVATE KEY-----" in result  # the fact of it remains visible
    assert "Rotate it." in result


def test_the_key_name_survives_so_the_operator_knows_what_to_rotate():
    result = redact_pii("ERROR password: sup3r-s3cret")
    assert "password" in result


def test_url_credentials_are_not_mislabelled_as_an_email():
    # The email pattern would otherwise claim `hunter2@sentry.io` first and
    # report a password as an email address.
    result = redact_pii("ERROR posting to https://svc:hunter2@sentry.io/42")
    assert "[REDACTED_EMAIL]" not in result
    assert "sentry.io" in result  # the host is diagnostic, keep it


@pytest.mark.parametrize(
    "text",
    [
        "ERROR Connection timeout to auth-service:8081 after 30000ms",
        "ERROR failed to parse config at /etc/app/settings.yaml line 12",
        "ERROR HTTP 500 Internal Server Error on POST /api/v1/charge",
        "WARN  token bucket refilled, rate=100/s",
    ],
)
def test_ordinary_log_lines_are_not_mangled(text):
    # A redactor that fires on normal traffic destroys the feature it is
    # protecting -- these must pass through untouched.
    assert redact_pii(text) == text
