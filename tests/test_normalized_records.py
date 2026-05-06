import json
from datetime import datetime
from zoneinfo import ZoneInfo

import pytest
import responses
from pydantic import BaseModel, ValidationError

from opinet import (
    FuelType,
    NormalizedFuelAverage,
    NormalizedFuelRegionCode,
    NormalizedFuelStation,
    ProductCode,
    to_json_safe_raw,
)

OPINET_BASE_URL = "https://www.opinet.co.kr/api/"


@responses.activate
def test_avg_price_to_normalized_record(client, load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", json=load_fixture("avg_all_price.json"))

    avg = client.get_national_average_price()[1]
    normalized = avg.to_normalized(endpoint="avgAllPrice.do")

    assert isinstance(normalized, NormalizedFuelAverage)
    assert isinstance(normalized, BaseModel)
    assert normalized.provider == "opinet"
    assert normalized.provider_endpoint == "avgAllPrice.do"
    assert normalized.provider_product_code == "B027"
    assert normalized.provider_product_name == avg.raw["PRODNM"]
    assert normalized.fuel_type is FuelType.GASOLINE
    assert normalized.price == pytest.approx(1667.33)
    assert normalized.diff == pytest.approx(-0.23)
    assert normalized.raw["PRICE"] == "1667.33"
    assert normalized.model_dump()["provider"] == "opinet"
    assert normalized.model_dump(mode="json")["trade_date"] == "2025-07-23"
    with pytest.raises(ValidationError):
        normalized.price = 0.0


def test_normalized_records_reject_extra_fields():
    with pytest.raises(ValidationError):
        NormalizedFuelRegionCode(
            provider_endpoint="areaCode.do",
            provider_region_code="01",
            provider_region_name="Seoul",
            code_level="sido",
            parent_sido_code=None,
            bjd_sido_prefix="11",
            raw={},
            extra_field="not allowed",
        )


@responses.activate
def test_avg_price_kst_datetime_and_timestamp(client, load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", json=load_fixture("avg_all_price.json"))

    avg = client.get_national_average_price()[0]
    normalized = avg.to_normalized()
    expected = datetime(2025, 7, 23, 0, 0, tzinfo=ZoneInfo("Asia/Seoul"))

    assert normalized.price_datetime() == expected
    assert normalized.price_timestamp() == pytest.approx(expected.timestamp())
    assert avg.price_datetime() == expected
    assert avg.price_timestamp() == pytest.approx(expected.timestamp())


@responses.activate
def test_station_to_normalized_record_without_provider_product_name(client, load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "lowTop10.do", json=load_fixture("low_top10_B027.json"))

    station = client.get_lowest_price_top20(ProductCode.GASOLINE, cnt=2, area="01")[0]
    normalized = station.to_normalized(endpoint="lowTop10.do")

    assert isinstance(normalized, NormalizedFuelStation)
    assert normalized.provider == "opinet"
    assert normalized.provider_endpoint == "lowTop10.do"
    assert normalized.provider_station_id == "A0013150"
    assert normalized.provider_station_name == station.name
    assert normalized.provider_product_code == "B027"
    assert normalized.provider_product_name is None
    assert normalized.fuel_type is FuelType.GASOLINE
    assert normalized.brand_code == "SKE"
    assert normalized.price == pytest.approx(1538.0)
    assert normalized.diff is None
    assert normalized.distance_m is None
    assert normalized.address_jibun == station.address_jibun
    assert normalized.address_road == station.address_road
    assert normalized.coordinates == station.coordinates
    assert normalized.katec_x == station.katec_x
    assert normalized.lon == station.lon
    assert normalized.trade_datetime() is None
    assert station.trade_datetime() is None
    assert normalized.raw["PRICE"] == "1538"


@responses.activate
def test_station_trade_datetime_when_trade_fields_exist(client, load_fixture):
    responses.add(
        responses.GET,
        OPINET_BASE_URL + "lowTop10.do",
        json=load_fixture("low_top10_with_trade_context.json"),
    )

    station = client.get_lowest_price_top20(ProductCode.GASOLINE, cnt=1)[0]
    normalized = station.to_normalized(endpoint="lowTop10.do")
    expected = datetime(2025, 7, 23, 14, 56, 18, tzinfo=ZoneInfo("Asia/Seoul"))

    assert normalized.provider_product_code == "D047"
    assert normalized.provider_product_name == "provider diesel"
    assert normalized.fuel_type is FuelType.DIESEL
    assert normalized.trade_datetime() == expected
    assert station.trade_datetime() == expected
    assert normalized.raw["TRADE_DT"] == "20250723"
    assert normalized.raw["TRADE_TM"] == "145618"


@responses.activate
def test_area_code_to_normalized_region_code(client, load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "areaCode.do", json=load_fixture("area_code_sido_01.json"))

    area = client.get_area_codes("01")[1]
    normalized = area.to_normalized()

    assert isinstance(normalized, NormalizedFuelRegionCode)
    assert normalized.provider == "opinet"
    assert normalized.provider_endpoint == "areaCode.do"
    assert normalized.provider_region_code == "0113"
    assert normalized.provider_region_name == area.name
    assert normalized.code_level == "sigungu"
    assert normalized.parent_sido_code == "01"
    assert normalized.bjd_sido_prefix == "11"
    assert normalized.raw["AREA_CD"] == "0113"


@responses.activate
def test_json_safe_raw_helper_converts_mapping_proxy_and_tuples(client, load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "detailById.do", json=load_fixture("detail_by_id_A0010207.json"))

    detail = client.get_station_detail("A0010207")
    raw = to_json_safe_raw(detail.raw)

    assert isinstance(raw, dict)
    assert isinstance(raw["OIL_PRICE"], list)
    assert raw["OIL_PRICE"][0]["PRICE"] == "1745"
    assert raw["OIL_PRICE"][0]["TRADE_TM"] == "145618"
    json.dumps(raw, ensure_ascii=False)
