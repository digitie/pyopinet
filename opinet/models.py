"""Dataclasses returned by the Opinet client."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, time

from .codes import BrandCode, ProductCode, StationType


@dataclass(frozen=True, slots=True)
class AvgPrice:
    trade_date: date
    product_code: ProductCode
    product_name: str
    price: float
    diff: float


@dataclass(frozen=True, slots=True)
class Station:
    uni_id: str
    name: str
    brand: BrandCode | None
    price: float | None
    address_jibun: str | None
    address_road: str | None
    katec_x: float
    katec_y: float
    lon: float
    lat: float
    distance_m: float | None = None


@dataclass(frozen=True, slots=True)
class OilPrice:
    product_code: ProductCode
    price: float | None
    trade_date: date
    trade_time: time


@dataclass(frozen=True, slots=True)
class StationDetail:
    uni_id: str
    name: str
    brand: BrandCode | None
    sub_brand: BrandCode | None
    station_type: StationType
    sigun_code: str
    address_jibun: str | None
    address_road: str | None
    tel: str | None
    katec_x: float
    katec_y: float
    lon: float
    lat: float
    has_maintenance: bool
    has_carwash: bool
    has_cvs: bool
    is_kpetro: bool
    prices: tuple[OilPrice, ...]


@dataclass(frozen=True, slots=True)
class AreaCode:
    code: str
    name: str

    @property
    def is_sido(self) -> bool:
        return len(self.code) == 2

    @property
    def is_sigungu(self) -> bool:
        return len(self.code) == 4
