"""Unofficial Python client for the Korean Opinet fuel price API."""

from .client import OpinetClient
from .codes import (
    BrandCode,
    ProductCode,
    SortOrder,
    StationType,
    bjd_sido_to_opinet,
    is_alddle,
    opinet_sido_to_bjd,
)
from .exceptions import (
    OpinetAuthError,
    OpinetError,
    OpinetInvalidParameterError,
    OpinetNetworkError,
    OpinetNoDataError,
    OpinetRateLimitError,
    OpinetServerError,
)
from .models import AreaCode, AvgPrice, OilPrice, Station, StationDetail

__all__ = [
    "AreaCode",
    "AvgPrice",
    "BrandCode",
    "OilPrice",
    "OpinetAuthError",
    "OpinetClient",
    "OpinetError",
    "OpinetInvalidParameterError",
    "OpinetNetworkError",
    "OpinetNoDataError",
    "OpinetRateLimitError",
    "OpinetServerError",
    "ProductCode",
    "SortOrder",
    "Station",
    "StationDetail",
    "StationType",
    "bjd_sido_to_opinet",
    "is_alddle",
    "opinet_sido_to_bjd",
]
