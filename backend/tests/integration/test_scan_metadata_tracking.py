from src.models.scan_metadata import ScanMetadata
from src.scanning.log_scan_service import run_log_scan
from src.scanning.scan_service import run_scan


def test_registry_scan_records_its_own_last_run_time(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])

    row = db_session.query(ScanMetadata).filter_by(scan_type="registry").one()
    assert row.last_run_at is not None


def test_log_scan_records_its_own_last_run_time_independently(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    run_log_scan(db_session, str(fixtures_dir / "logs"))

    # Two distinct rows -- a log scan must not overwrite the registry
    # scan's own recorded time, or vice versa.
    assert db_session.query(ScanMetadata).filter_by(scan_type="registry").one() is not None
    assert db_session.query(ScanMetadata).filter_by(scan_type="log").one() is not None
    assert db_session.query(ScanMetadata).count() == 2


def test_rescan_advances_the_existing_row_rather_than_duplicating(db_session, fixtures_dir):
    run_scan(db_session, [str(fixtures_dir / "repo-node")])
    first_run_at = db_session.query(ScanMetadata).filter_by(scan_type="registry").one().last_run_at

    run_scan(db_session, [str(fixtures_dir / "repo-node")])

    rows = db_session.query(ScanMetadata).filter_by(scan_type="registry").all()
    assert len(rows) == 1
    assert rows[0].last_run_at >= first_run_at
