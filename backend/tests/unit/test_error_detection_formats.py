"""Log formats that occur in real production estates.

An audit against realistic input found the detector reporting 11 false
errors out of 31 ordinary INFO/DEBUG lines, collapsing every JSON log line
in a file into one meaningless group, and dropping the informative line of
every stack trace. These tests pin the corrected behaviour.
"""

import pytest

from src.scanning.error_detection import detect_errors, extract_timestamp
from src.scanning.normalization import normalize_template


@pytest.mark.parametrize(
    "line",
    [
        "INFO Registered global exception handler",
        'INFO 127.0.0.1 - GET /api/error?x=1 HTTP/1.1 200',
        "INFO Retrying request after error, attempt 2",
        "INFO config: log_level=error",
        "DEBUG Building error page cache",
        "INFO this is a critical path optimisation",
        "INFO Server started; error reporting disabled",
        "INFO Sentry error tracking initialised",
        "INFO GET /healthz -> 200 (no exception)",
        "INFO Documentation: see docs/error-codes.md",
        '{"level":"info","msg":"registered exception handler"}',
    ],
)
def test_a_line_that_declares_a_non_error_level_is_not_an_error(line):
    # The level a line declares about itself outranks any alarming word in
    # its message. Without this the tool reported baseline noise on every
    # service, in red, and got switched off.
    assert detect_errors([line]) == []


@pytest.mark.parametrize(
    "line, expected_marker",
    [
        ("ERROR plain message", "ERROR"),
        ("2024-05-01 10:00:00,123 ERROR [main] c.f.Svc - boom", "ERROR"),
        ("ERR upstream timed out", "ERROR"),  # nginx/haproxy
        ("E0101 00:00:00 controller.go:10] sync failed", "ERROR"),  # klog
        ("E! [outputs.influxdb] write failed", "ERROR"),  # telegraf
        ("level=error msg=\"connection refused\"", "ERROR"),  # logfmt
        ("ValueError: bad input", "ERROR"),  # bare exception class
        ('{"level":"fatal","msg":"ledger checksum mismatch"}', "FATAL"),
    ],
)
def test_real_error_lines_are_detected_with_the_right_severity(line, expected_marker):
    entries = detect_errors([line])
    assert len(entries) == 1
    assert entries[0].severity_marker == expected_marker


def test_json_logs_group_by_message_not_by_key_arity():
    # Templating the whole JSON object made every line in a file collapse
    # into one group keyed only on how many keys it had -- hiding, among
    # other things, a FATAL data-loss event behind an INFO example.
    lines = [
        '{"level":"info","ts":"2024-05-01T10:00:00Z","msg":"server listening"}',
        '{"level":"error","ts":"2024-05-01T10:00:02Z","msg":"stripe charge declined"}',
        '{"level":"error","ts":"2024-05-01T10:00:03Z","msg":"postgres connection refused"}',
        '{"level":"error","ts":"2024-05-01T10:00:04Z","msg":"postgres connection refused"}',
        '{"level":"fatal","ts":"2024-05-01T10:00:05Z","msg":"ledger checksum mismatch"}',
    ]

    entries = detect_errors(lines)
    templates = {normalize_template(e.message) for e in entries}

    assert len(entries) == 4  # the INFO line is not one of them
    assert templates == {
        "stripe charge declined",
        "postgres connection refused",
        "ledger checksum mismatch",
    }
    assert any(e.severity_marker == "FATAL" for e in entries)


def test_json_timestamp_is_found_even_though_it_is_not_at_column_zero():
    entry = detect_errors(['{"level":"error","ts":"2024-05-01T10:00:00Z","msg":"x"}'])[0]

    assert extract_timestamp(entry.first_line, entry.structured_timestamp) is not None


def test_timezone_offset_is_converted_not_discarded():
    # Truncating the offset made a container logging in +02:00 appear two
    # hours away from a UTC one for the same instant.
    utc = extract_timestamp("", "2024-05-01T08:00:00Z")
    berlin = extract_timestamp("", "2024-05-01T10:00:00+02:00")

    assert utc == berlin  # the same instant


def test_python_traceback_keeps_the_exception_line():
    lines = [
        "Traceback (most recent call last):",
        '  File "/app/svc.py", line 42, in handle',
        "    return do_work(payload)",
        "KeyError: 'id'",
    ]

    entries = detect_errors(lines)

    assert len(entries) == 1  # one incident, not two
    assert "KeyError: 'id'" in entries[0].raw_text  # the informative line survives


def test_java_stack_trace_is_one_entry_including_its_cause():
    lines = [
        "2024-05-01 10:00:01,002 ERROR [exec-1] c.f.OrderService - Failed to place order 10231",
        'java.lang.NullPointerException: Cannot invoke "Order.getId()" because "order" is null',
        "\tat com.foo.OrderService.process(OrderService.java:88)",
        "Caused by: java.sql.SQLException: connection closed",
        "\tat org.postgresql.Driver.connect(Driver.java:12)",
    ]

    entries = detect_errors(lines)

    assert len(entries) == 1
    text = entries[0].raw_text
    assert "NullPointerException" in text
    assert "Caused by: java.sql.SQLException" in text  # the root cause survives


def test_different_tracebacks_do_not_all_merge_into_one_group():
    def traceback_for(exc: str) -> list[str]:
        return ["Traceback (most recent call last):", '  File "/app/x.py", line 1', exc]

    entries = detect_errors(
        traceback_for("KeyError: 'id'")
        + traceback_for("ZeroDivisionError: division by zero")
    )
    templates = {normalize_template(e.raw_text) for e in entries}

    assert len(templates) == 2
