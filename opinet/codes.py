"""Enums and code mappings used by the Opinet API."""

from __future__ import annotations

from enum import StrEnum

from .exceptions import OpinetInvalidParameterError


class ProductCode(StrEnum):
    """Opinet product codes."""

    GASOLINE = "B027"
    GASOLINE_PREMIUM = "B034"
    DIESEL = "D047"
    KEROSENE = "C004"
    LPG = "K015"


class BrandCode(StrEnum):
    """Opinet brand codes."""

    SKE = "SKE"
    GSC = "GSC"
    HDO = "HDO"
    SOL = "SOL"
    RTE = "RTE"
    RTX = "RTX"
    NHO = "NHO"
    ETC = "ETC"
    E1G = "E1G"
    SKG = "SKG"


class SortOrder(StrEnum):
    """Search sorting options."""

    PRICE = "1"
    DISTANCE = "2"


class StationType(StrEnum):
    """Station type encoded by the API's LPG_YN field."""

    GAS_STATION = "N"
    LPG_STATION = "Y"
    BOTH = "C"


ALDDLE_BRANDS = frozenset({BrandCode.RTE, BrandCode.RTX, BrandCode.NHO})

OPINET_TO_BJD: dict[str, str] = {
    "01": "11",
    "02": "41",
    "03": "42",
    "04": "43",
    "05": "44",
    "06": "45",
    "07": "46",
    "08": "47",
    "09": "48",
    "10": "26",
    "11": "50",
    "14": "27",
    "15": "28",
    "16": "29",
    "17": "30",
    "18": "31",
    "19": "36",
}

BJD_TO_OPINET: dict[str, str] = {value: key for key, value in OPINET_TO_BJD.items()}
BJD_LEGACY_TO_NEW: dict[str, str] = {"42": "51", "45": "52"}
BJD_NEW_TO_LEGACY: dict[str, str] = {value: key for key, value in BJD_LEGACY_TO_NEW.items()}


def is_alddle(brand: BrandCode | str | None) -> bool:
    """Return whether a brand code belongs to an alddle station."""
    if brand is None:
        return False
    try:
        return BrandCode(brand) in ALDDLE_BRANDS
    except ValueError:
        return False


def opinet_sido_to_bjd(opinet_code: str) -> str:
    """Convert a 2-digit Opinet sido code to a BJD sido prefix."""
    if opinet_code not in OPINET_TO_BJD:
        raise OpinetInvalidParameterError(
            f"unknown opinet sido code: {opinet_code!r}. Valid codes are 01-11 and 14-19."
        )
    return OPINET_TO_BJD[opinet_code]


def bjd_sido_to_opinet(bjd_code: str) -> str:
    """Convert a 2-digit BJD sido prefix to an Opinet sido code."""
    normalized = BJD_NEW_TO_LEGACY.get(bjd_code, bjd_code)
    if normalized not in BJD_TO_OPINET:
        raise OpinetInvalidParameterError(f"unknown BJD sido code: {bjd_code!r}")
    return BJD_TO_OPINET[normalized]
