from src.scanning.error_detection import MAX_CONTINUATION_LINES, SEVERITY_MARKERS, detect_errors


def test_each_severity_marker_matches_case_insensitively():
    for marker in SEVERITY_MARKERS:
        lines = [f"2026-01-01 00:00:00 {marker.lower()} something went wrong"]
        entries = detect_errors(lines)
        assert len(entries) == 1
        assert entries[0].severity_marker == marker


def test_continuation_lines_captured_into_same_entry():
    lines = [
        "2026-01-01 00:00:00 ERROR boom",
        "  at foo (a.js:1)",
        "  at bar (b.js:2)",
        "  Caused by: Something",
        "    at baz (c.js:3)",
        "2026-01-01 00:00:01 INFO next",
    ]
    entries = detect_errors(lines)
    assert len(entries) == 1
    assert entries[0].continuation_lines == lines[1:5]


def test_capture_stops_at_blank_line():
    lines = ["ERROR boom", "  at foo", "", "  at bar (not captured)"]
    entries = detect_errors(lines)
    assert entries[0].continuation_lines == ["  at foo"]


def test_capture_stops_at_new_error_marker():
    lines = ["ERROR first", "  at foo", "FATAL second", "  at bar"]
    entries = detect_errors(lines)
    assert len(entries) == 2
    assert entries[0].continuation_lines == ["  at foo"]
    assert entries[1].continuation_lines == ["  at bar"]


def test_capture_stops_at_non_continuation_line():
    lines = ["ERROR boom", "this is not indented or an at/file/caused-by line"]
    entries = detect_errors(lines)
    assert entries[0].continuation_lines == []


def test_capture_respects_max_line_cap():
    lines = ["ERROR boom"] + [f"  line {i}" for i in range(500)]
    entries = detect_errors(lines)
    assert len(entries[0].continuation_lines) == MAX_CONTINUATION_LINES


def test_lines_with_no_marker_produce_no_entries():
    assert detect_errors(["INFO all good", "DEBUG fine too"]) == []
