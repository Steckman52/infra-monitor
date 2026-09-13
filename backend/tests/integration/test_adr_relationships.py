import shutil

from src.models.adr_record import AdrRecord
from src.models.adr_relationship import AdrRelationship
from src.models.adr_service_association import AdrServiceAssociation
from src.scanning.scan_service import run_scan


def test_relationship_dedup_and_service_association(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "adr-repo")])

    relationships = db_session.query(AdrRelationship).all()
    assert len(relationships) == 1  # dedup despite both-sided mention (0002/0003)
    rel = relationships[0]
    assert rel.from_adr.title == "Third Decision"
    assert rel.to_adr.title == "Second Decision"
    assert rel.relationship_type == "supersedes"

    adr_count = db_session.query(AdrRecord).count()
    associations = db_session.query(AdrServiceAssociation).all()
    assert adr_count == 4
    # every ADR in this monorepo relates to both services (research.md §7, SC-005)
    assert len(associations) == adr_count * 2


def test_rescan_drops_relationship_after_target_deleted(tmp_path, db_session, fixtures_dir):
    scratch = tmp_path / "adr-repo"
    shutil.copytree(fixtures_dir / "adr-repo", scratch)

    run_scan(db_session, [str(scratch)])
    assert db_session.query(AdrRelationship).count() == 1

    (scratch / "docs" / "adr" / "0003-third-decision.md").unlink()
    run_scan(db_session, [str(scratch)])

    assert db_session.query(AdrRelationship).count() == 0
