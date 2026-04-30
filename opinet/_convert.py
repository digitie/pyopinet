"""Type conversion helpers for raw Opinet API values."""

from __future__ import annotations

from datetime import date, datetime, time
from typing import Any


def to_date(value: Any) -> date | None:
    """Convert YYYYMMDD values to ``date`` while preserving blanks as ``None``."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    text = str(value).strip()
    if len(text) != 8 or not text.isdigit():
        raise ValueError(f"invalid YYYYMMDD: {text!r}")
    return datetime.strptime(text, "%Y%m%d").date()


def to_time(value: Any) -> time | None:
    """Convert HHMMSS values to ``time`` while preserving blanks as ``None``."""
    if value is None or (isinstance(value, str) and not value.strip()):
        return None
    text = str(value).strip()
    if len(text) != 6 or not text.isdigit():
        raise ValueError(f"invalid HHMMSS: {text!r}")
    return datetime.strptime(text, "%H%M%S").time()


def to_float_or_none(value: Any) -> float | None:
    """Convert numeric strings, including signed values, to ``float``."""
    if value is None:
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    return float(text)


def to_bool_yn(value: Any) -> bool:
    """Convert Opinet Y/N flags to ``bool``."""
    if value is None:
        return False
    return str(value).strip().upper() == "Y"


def strip_or_none(value: Any) -> str | None:
    """Strip string-like values and normalize blanks to ``None``."""
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None
