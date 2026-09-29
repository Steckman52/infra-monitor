from src.analysis.version_compatibility import status_for_majors


def test_same_major_is_compatible():
    status, has_not_comparable = status_for_majors([4, 4, 4])
    assert status == "compatible"
    assert has_not_comparable is False


def test_differing_major_is_a_risk():
    status, has_not_comparable = status_for_majors([4, 3])
    assert status == "compatibility_risk"
    assert has_not_comparable is False


def test_not_comparable_entry_flagged_independently_of_status():
    # Only one comparable major present -> vacuously compatible among the
    # comparable entries, but the not-comparable entry must still be flagged.
    status, has_not_comparable = status_for_majors([4, None])
    assert status == "compatible"
    assert has_not_comparable is True


def test_risk_and_not_comparable_can_coexist():
    status, has_not_comparable = status_for_majors([4, 3, None])
    assert status == "compatibility_risk"
    assert has_not_comparable is True


def test_all_not_comparable_is_unknown_not_compatible():
    # FR-005: with nothing readable there is no agreement to report. Real
    # Maven modules inherit nearly every version from a parent POM, so this
    # is the common case for Java -- reporting it green would assert
    # compatibility between versions that were never read.
    status, has_not_comparable = status_for_majors([None, None])
    assert status == "unknown"
    assert has_not_comparable is True


def test_single_comparable_entry_is_still_compatible():
    # One readable version among unreadable ones is a real (if weak)
    # verdict: nothing contradicts it. Only a total absence is "unknown".
    status, has_not_comparable = status_for_majors([(4,), None])
    assert status == "compatible"
    assert has_not_comparable is True
