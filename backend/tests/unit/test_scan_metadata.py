from datetime import datetime, timezone

from src.models.scan_metadata import ScanMetadata, record_scan


def test_record_scan_inserts_a_new_row_when_none_exists(db_session):
    timestamp = datetime(2026, 1, 1, tzinfo=timezone.utc)

    record_scan(db_session, "registry", timestamp)
    db_session.commit()

    row = db_session.query(ScanMetadata).filter_by(scan_type="registry").one()
    assert row.last_run_at.replace(tzinfo=timezone.utc) == timestamp


def test_record_scan_updates_the_existing_row_in_place(db_session):
    first = datetime(2026, 1, 1, tzinfo=timezone.utc)
    second = datetime(2026, 1, 2, tzinfo=timezone.utc)

    record_scan(db_session, "registry", first)
    db_session.commit()
    record_scan(db_session, "registry", second)
    db_session.commit()

    rows = db_session.query(ScanMetadata).filter_by(scan_type="registry").all()
    assert len(rows) == 1
    assert rows[0].last_run_at.replace(tzinfo=timezone.utc) == second


def test_registry_and_log_scan_types_tracked_independently(db_session):
    registry_time = datetime(2026, 1, 1, tzinfo=timezone.utc)
    log_time = datetime(2026, 1, 2, tzinfo=timezone.utc)

    record_scan(db_session, "registry", registry_time)
    record_scan(db_session, "log", log_time)
    db_session.commit()

    registry_row = db_session.query(ScanMetadata).filter_by(scan_type="registry").one()
    log_row = db_session.query(ScanMetadata).filter_by(scan_type="log").one()
    assert registry_row.last_run_at.replace(tzinfo=timezone.utc) == registry_time
    assert log_row.last_run_at.replace(tzinfo=timezone.utc) == log_time
