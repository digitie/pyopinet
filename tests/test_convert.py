from datetime import date, time

import pytest

from opinet._convert import strip_or_none, to_bool_yn, to_date, to_float_or_none, to_time


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("20250723", date(2025, 7, 23)),
        ("19000101", date(1900, 1, 1)),
    ],
)
def test_to_date_valid(value, expected):
    result = to_date(value)
    assert result == expected
    assert isinstance(result, date)


@pytest.mark.parametrize("value", [None, "", "   "])
def test_to_date_empty(value):
    assert to_date(value) is None


@pytest.mark.parametrize("value", ["2025-07-23", "20250732", "2025723", "abc"])
def test_to_date_invalid(value):
    with pytest.raises(ValueError):
        to_date(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("145618", time(14, 56, 18)),
        ("000000", time(0, 0, 0)),
        ("235959", time(23, 59, 59)),
    ],
)
def test_to_time_valid(value, expected):
    result = to_time(value)
    assert result == expected
    assert isinstance(result, time)


@pytest.mark.parametrize("value", [None, "", "   "])
def test_to_time_empty(value):
    assert to_time(value) is None


@pytest.mark.parametrize("value", ["14:56:18", "246001", "12345", "abc"])
def test_to_time_invalid(value):
    with pytest.raises(ValueError):
        to_time(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("1745", 1745.0),
        ("1919.44", 1919.44),
        ("+0.39", 0.39),
        ("-0.10", -0.10),
        (1745, 1745.0),
        (1919.44, 1919.44),
    ],
)
def test_to_float_valid(value, expected):
    result = to_float_or_none(value)
    assert result == pytest.approx(expected)
    assert isinstance(result, float)


@pytest.mark.parametrize("value", [None, "", "   "])
def test_to_float_empty(value):
    assert to_float_or_none(value) is None


@pytest.mark.parametrize("value", ["abc", object()])
def test_to_float_invalid(value):
    with pytest.raises(ValueError):
        to_float_or_none(value)


@pytest.mark.parametrize(
    ("value", "expected"),
    [("Y", True), ("y", True), ("N", False), ("n", False), ("", False), (None, False), ("X", False)],
)
def test_to_bool_yn(value, expected):
    assert to_bool_yn(value) is expected


@pytest.mark.parametrize(
    ("value", "expected"),
    [(None, None), ("", None), (" ", None), (" hello ", "hello"), (123, "123")],
)
def test_strip_or_none(value, expected):
    assert strip_or_none(value) == expected
