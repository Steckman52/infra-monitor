import pytest

from src.analysis.version_compatibility import extract_major_version


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
