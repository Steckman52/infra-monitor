import pytest

from src.analysis.version_compatibility import extract_effective_version, extract_major_version


@pytest.mark.parametrize(
    "declared_version, expected_major",
    [
        ("^4.18.0", 4),
        ("~1.5.0", 1),
        (">=2.31.0", 2),
        ("v1.9.1", 1),
        ("5.3.20", 5),
        ("${hamcrestVersion}", None),
        ("workspace:*", None),
        (None, None),
    ],
)
def test_extract_major_version(declared_version, expected_major):
    assert extract_major_version(declared_version) == expected_major


@pytest.mark.parametrize(
    "declared_version, expected",
    [
        ("^4.18.0", (4,)),  # nonzero major: minor doesn't matter
        ("~1.5.0", (1,)),
        (">=0.104.0", (0, 104)),  # major 0: minor is the real comparability unit
        ("==0.115.0", (0, 115)),
        (">=0.110.0", (0, 110)),
        ("0", (0,)),  # major 0 with no minor to read
        ("${hamcrestVersion}", None),
        ("workspace:*", None),
        (None, None),
    ],
)
def test_extract_effective_version(declared_version, expected):
    assert extract_effective_version(declared_version) == expected
