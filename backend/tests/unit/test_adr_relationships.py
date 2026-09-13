from src.models.adr_record import AdrRecord
from src.scanning.adr_relationships import resolve_relationships


def _record(tmp_path, filename, title, content):
    return AdrRecord(
        title=title,
        raw_status=None,
        normalized_status="accepted",
        date=None,
        source_path=str(tmp_path / "docs" / "adr" / filename),
        repository_path=str(tmp_path),
        content=content,
        has_secret_warning=False,
    )


def test_all_four_keyword_phrases_produce_relationships(tmp_path):
    a = _record(tmp_path, "0001-a.md", "A", "# A\n\n* Status: accepted\n")
    b = _record(tmp_path, "0002-b.md", "B", "# B\n\nSupersedes [A](0001-a.md)\n")
    c = _record(tmp_path, "0003-c.md", "C", "# C\n\n* Status: superseded by [B](0002-b.md)\n")
    d = _record(tmp_path, "0004-d.md", "D", "# D\n\nAmends [A](0001-a.md)\n")
    e = _record(tmp_path, "0005-e.md", "E", "# E\n\nAmended by [D](0004-d.md)\n")

    relationships = resolve_relationships([a, b, c, d, e])

    by_triple = {(r.from_adr.title, r.to_adr.title, r.relationship_type) for r in relationships}
    assert ("B", "A", "supersedes") in by_triple
    assert ("B", "C", "supersedes") in by_triple
    assert ("D", "A", "amends") in by_triple
    assert ("D", "E", "amends") in by_triple


def test_both_sided_mention_dedups_to_one(tmp_path):
    old = _record(
        tmp_path, "0002-old.md", "Old", "# Old\n\n* Status: superseded by [New](0003-new.md)\n"
    )
    new = _record(
        tmp_path,
        "0003-new.md",
        "New",
        "# New\n\n* Status: accepted\n\n## Links\n\n* Supersedes [Old](0002-old.md)\n",
    )

    relationships = resolve_relationships([old, new])

    assert len(relationships) == 1
    rel = relationships[0]
    assert rel.from_adr.title == "New"
    assert rel.to_adr.title == "Old"
    assert rel.relationship_type == "supersedes"


def test_link_to_missing_file_produces_no_relationship(tmp_path):
    record = _record(
        tmp_path, "0001-a.md", "A", "# A\n\n* Status: superseded by [Ghost](9999-ghost.md)\n"
    )

    relationships = resolve_relationships([record])

    assert relationships == []
