import re
from pathlib import Path

from src.models.adr_record import AdrRecord
from src.models.adr_relationship import AdrRelationship

_RELATIONSHIP_RE = re.compile(
    r"(?i)\b(supersedes|superseded by|amends|amended by)\b[^\n]*?\[[^\]]*\]\(([^)]+)\)"
)


def resolve_relationships(adr_records: list[AdrRecord]) -> list[AdrRelationship]:
    """Detect supersedes/amends relationships across `adr_records`
    (research.md §5-6): search each record's full content for a keyword
    phrase followed on the same line by a Markdown link, resolve the link
    target by path against the other records in this same scan, and
    normalize both phrasings of a relationship ("supersedes" said by the
    new ADR, "superseded by" said by the old one) to the same canonical
    (from, to, type) tuple so a both-sided mention dedupes to one row."""
    records_by_path = {Path(record.source_path).resolve(): record for record in adr_records}
    seen: set[tuple[str, str, str]] = set()
    relationships: list[AdrRelationship] = []

    for record in adr_records:
        record_dir = Path(record.source_path).resolve().parent
        for match in _RELATIONSHIP_RE.finditer(record.content):
            keyword = match.group(1).lower()
            link_target = match.group(2)
            target_path = (record_dir / link_target).resolve()
            target_record = records_by_path.get(target_path)
            if target_record is None or target_record is record:
                continue  # research.md §6: no match in this scan, no relationship row

            if keyword == "supersedes":
                from_record, to_record, relationship_type = record, target_record, "supersedes"
            elif keyword == "superseded by":
                from_record, to_record, relationship_type = target_record, record, "supersedes"
            elif keyword == "amends":
                from_record, to_record, relationship_type = record, target_record, "amends"
            else:  # "amended by"
                from_record, to_record, relationship_type = target_record, record, "amends"

            dedup_key = (from_record.source_path, to_record.source_path, relationship_type)
            if dedup_key in seen:
                continue
            seen.add(dedup_key)

            relationship = AdrRelationship(relationship_type=relationship_type)
            relationship.from_adr = from_record
            relationship.to_adr = to_record
            relationships.append(relationship)

    return relationships
