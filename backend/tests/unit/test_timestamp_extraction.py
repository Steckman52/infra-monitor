from datetime import datetime

from src.scanning.error_detection import extract_timestamp


def test_extracts_iso8601():
    assert extract_timestamp("2026-09-11T08:47:00 ERROR boom") == datetime(2026, 9, 11, 8, 47, 0)


def test_extracts_common_log_format():
    assert extract_timestamp("2026-09-11 08:47:00 ERROR boom") == datetime(2026, 9, 11, 8, 47, 0)


def test_unrecognized_format_returns_none():
    assert extract_timestamp("[Sep 11 08:47:00] ERROR boom") is None
