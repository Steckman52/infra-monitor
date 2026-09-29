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


@pytest.mark.parametrize(
    "spec",
    [
        ">=1.19",           # the normal way to declare a dep in setup.py
        ">=1.0.0 <3.0.0",   # spans two majors
        "<2.0.0",
        "[1.0,)",           # Maven, open-ended
        "^1.0.0 || ^2.0.0", # npm OR range
    ],
)
def test_a_spec_admitting_several_majors_is_not_comparable(spec):
    # Such a spec pins nothing, so comparing it to a concrete version
    # answers a question it was never asked -- and produced red
    # "compatibility risk" rows for dependencies that resolve fine.
    assert extract_effective_version(spec) is None


@pytest.mark.parametrize(
    "spec, expected",
    [
        ("[1.0,2.0)", (1,)),   # bounded inside one major: still comparable
        ("^2.1.0", (2,)),
        (">=0.104.0", (0, 104)),  # pre-1.0: the 0.x minor rule still applies
    ],
)
def test_specs_that_do_pin_a_major_stay_comparable(spec, expected):
    assert extract_effective_version(spec) == expected
