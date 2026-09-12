from datetime import date

import pytest

from src.scanning.parsed_manifest import ManifestParseError
from src.scanning.parsers import adr_markdown


def test_extracts_title_status_date(tmp_path):
    path = tmp_path / "0001-x.md"
    path.write_text(
        "# My Decision\n\n* Status: accepted\n* Date: 2026-01-01\n\n## Context\n...\n",
        encoding="utf-8",
    )

    result = adr_markdown.parse(path)

    assert result.title == "My Decision"
    assert result.raw_status == "accepted"
    assert result.normalized_status == "accepted"
    assert result.date == date(2026, 1, 1)


def test_missing_title_raises(tmp_path):
    path = tmp_path / "broken.md"
    path.write_text("Just text, no title.\n\n* Status: accepted\n", encoding="utf-8")

    with pytest.raises(ManifestParseError):
        adr_markdown.parse(path)


def test_missing_date_is_none(tmp_path):
    path = tmp_path / "0001-x.md"
    path.write_text("# Title\n\n* Status: accepted\n", encoding="utf-8")

    result = adr_markdown.parse(path)

    assert result.date is None


def test_missing_status_is_unrecognized(tmp_path):
    path = tmp_path / "0001-x.md"
    path.write_text("# Title\n\nNo status line here.\n", encoding="utf-8")

    result = adr_markdown.parse(path)

    assert result.raw_status is None
    assert result.normalized_status == "unrecognized"


@pytest.mark.parametrize(
    "raw_status, expected_category",
    [
        ("accepted", "accepted"),
        ("proposed", "proposed"),
        ("rejected", "rejected"),
        ("deprecated", "deprecated"),
        ("superseded by [0005](0005.md)", "superseded"),
        ("accepted but later superseded by [0005](0005.md)", "superseded"),
        ("something else entirely", "unrecognized"),
    ],
)
def test_status_normalization_priority(tmp_path, raw_status, expected_category):
    path = tmp_path / "0001-x.md"
    path.write_text(f"# Title\n\n* Status: {raw_status}\n", encoding="utf-8")

    result = adr_markdown.parse(path)

    assert result.normalized_status == expected_category
