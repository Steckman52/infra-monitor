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


def test_all_not_comparable_is_vacuously_compatible_but_flagged():
    status, has_not_comparable = status_for_majors([None, None])
    assert status == "compatible"
    assert has_not_comparable is True
