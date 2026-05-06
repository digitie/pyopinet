"""Application-facing normalized records for Opinet response models."""

from __future__ import annotations

from collections.abc import Mapping as MappingABC
from dataclasses import dataclass, field
from datetime import date, datetime, time, tzinfo
from enum import Enum
from typing import Any, Literal, TypeAlias, TYPE_CHECKING
from zoneinfo import ZoneInfo

from .codes import FuelType
from .models import StationCoordinates

if TYPE_CHECKING:
    from .models import AreaCode, AvgPrice, Station

JsonValue: TypeAlias = None | bool | int | float | str | list["JsonValue"] | dict[str, "JsonValue"]

PROVIDER: Literal["opinet"] = "opinet"
DEFAULT_TIMEZONE = "Asia/Seoul"


def _coerce_tz(tz: str | tzinfo = DEFAULT_TIMEZONE) -> tzinfo:
    if isinstance(tz, str):
        return ZoneInfo(tz)
    return tz


def to_json_safe_raw(value: Any) -> JsonValue:
    """Convert raw payload values to JSON-safe plain dict/list structures."""
    if value is None or isinstance(value, bool | int | float | str):
        return value
    if isinstance(value, Enum):
        return str(value.value)
    if isinstance(value, datetime | date | time):
        return value.isoformat()
    if isinstance(value, MappingABC):
        return {str(key): to_json_safe_raw(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set | frozenset):
        return [to_json_safe_raw(item) for item in value]
    return str(value)


raw_to_json_safe = to_json_safe_raw


@dataclass(frozen=True, slots=True)
class NormalizedFuelAverage:
    """Normalized national average fuel price record."""

    provider: Literal["opinet"] = field(default=PROVIDER, init=False)
    provider_endpoint: str
    provider_product_code: str
    provider_product_name: str
    fuel_type: FuelType
    trade_date: date
    price: float
    diff: float
    raw: dict[str, JsonValue]

    def price_datetime(self, tz: str | tzinfo = DEFAULT_TIMEZONE) -> datetime:
        """Return the price date as timezone-aware midnight in the given timezone."""
        return datetime.combine(self.trade_date, time.min, tzinfo=_coerce_tz(tz))

    def price_timestamp(self, tz: str | tzinfo = DEFAULT_TIMEZONE) -> float:
        """Return ``price_datetime(tz).timestamp()``."""
        return self.price_datetime(tz).timestamp()


@dataclass(frozen=True, slots=True)
class NormalizedFuelStation:
    """Normalized fuel station price/search record."""

    provider: Literal["opinet"] = field(default=PROVIDER, init=False)
    provider_endpoint: str
    provider_station_id: str
    provider_station_name: str
    provider_product_code: str | None
    provider_product_name: str | None
    fuel_type: FuelType
    brand_code: str | None
    price: float | None
    diff: float | None
    distance_m: float | None
    address_jibun: str | None
    address_road: str | None
    coordinates: StationCoordinates
    katec_x: float
    katec_y: float
    lon: float
    lat: float
    trade_date: date | None
    trade_time: time | None
    raw: dict[str, JsonValue]

    def trade_datetime(self, tz: str | tzinfo = DEFAULT_TIMEZONE) -> datetime | None:
        """Return a timezone-aware trade datetime when both date and time are available."""
        if self.trade_date is None or self.trade_time is None:
            return None
        return datetime.combine(self.trade_date, self.trade_time, tzinfo=_coerce_tz(tz))


@dataclass(frozen=True, slots=True)
class NormalizedFuelRegionCode:
    """Normalized Opinet region code record."""

    provider: Literal["opinet"] = field(default=PROVIDER, init=False)
    provider_endpoint: str
    provider_region_code: str
    provider_region_name: str
    code_level: Literal["sido", "sigungu"]
    parent_sido_code: str | None
    bjd_sido_prefix: str
    raw: dict[str, JsonValue]


def normalize_average(avg: AvgPrice, *, endpoint: str = "avgAllPrice.do") -> NormalizedFuelAverage:
    """Build a normalized average-price record from ``AvgPrice``."""
    return NormalizedFuelAverage(
        provider_endpoint=endpoint,
        provider_product_code=avg.provider_product_code,
        provider_product_name=avg.provider_product_name,
        fuel_type=avg.fuel_type,
        trade_date=avg.trade_date,
        price=avg.price,
        diff=avg.diff,
        raw=_json_safe_raw_dict(avg.raw),
    )


def normalize_station(station: Station, *, endpoint: str) -> NormalizedFuelStation:
    """Build a normalized station record from ``Station``."""
    return NormalizedFuelStation(
        provider_endpoint=endpoint,
        provider_station_id=station.provider_station_id,
        provider_station_name=station.name,
        provider_product_code=station.provider_product_code,
        provider_product_name=station.provider_product_name,
        fuel_type=station.fuel_type,
        brand_code=station.brand_code,
        price=station.price,
        diff=None,
        distance_m=station.distance_m,
        address_jibun=station.address_jibun,
        address_road=station.address_road,
        coordinates=station.coordinates,
        katec_x=station.katec_x,
        katec_y=station.katec_y,
        lon=station.lon,
        lat=station.lat,
        trade_date=station.trade_date,
        trade_time=station.trade_time,
        raw=_json_safe_raw_dict(station.raw),
    )


def normalize_region_code(area: AreaCode, *, endpoint: str = "areaCode.do") -> NormalizedFuelRegionCode:
    """Build a normalized region-code record from ``AreaCode``."""
    return NormalizedFuelRegionCode(
        provider_endpoint=endpoint,
        provider_region_code=area.code,
        provider_region_name=area.name,
        code_level=area.code_level,
        parent_sido_code=area.parent_sido_code,
        bjd_sido_prefix=area.bjd_sido_prefix,
        raw=_json_safe_raw_dict(area.raw),
    )


def _json_safe_raw_dict(raw: Any) -> dict[str, JsonValue]:
    converted = to_json_safe_raw(raw)
    if isinstance(converted, dict):
        return converted
    return {"value": converted}
