"""오피넷 디버그 fixture 생성을 위한 Streamlit 예제 앱."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if SRC_DIR.exists() and str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st
from kraddr.base import KatecPoint, PlaceCoordinate

from opinet import OpinetClient, ProductCode, SortOrder, get_api_catalog_item, get_api_catalog_options
from opinet.debug import DebugRun, jsonable, save_debug_fixture


def main() -> None:
    """Streamlit 디버그 앱을 실행한다."""
    st.set_page_config(page_title="Opinet Debug", layout="wide")

    options = get_api_catalog_options()
    selected = st.sidebar.selectbox("API", options, format_func=lambda option: option["label"])
    catalog_item = get_api_catalog_item(selected["value"])
    st.sidebar.link_button("서비스키 발급", catalog_item.service_key_url)
    api_key = st.sidebar.text_input("서비스키", type="password")

    client = OpinetClient(api_key=api_key or None, retry_backoff=0)
    debug_client = client.debug()

    run: DebugRun | None = st.session_state.get("last_run")
    with st.form("debug_form"):
        inputs = _render_inputs(selected["value"])
        submitted = st.form_submit_button("실행")
        if submitted:
            run = _run_debug(debug_client, selected["value"], inputs)
            st.session_state["last_run"] = run

    if run is None:
        st.json(catalog_item.to_dict())
        return

    raw_tab, parsed_tab, processed_tab, error_tab, trace_tab, fixture_tab = st.tabs(
        ["Raw Response", "Parsed", "Processed", "Validation Errors", "Debug Trace", "Fixture/Testcase"]
    )
    raw_tab.json(run.response)
    parsed_tab.json(jsonable(run.parsed))
    processed_tab.json(jsonable(run.processed))
    error_tab.json(run.error or {})
    with trace_tab:
        st.markdown(f"**데이터셋:** {run.dataset_name}")
        st.link_button("서비스키 발급", run.service_key_url)
        st.json(run.trace_payload)
    _render_fixture_tab(fixture_tab, run)


def _render_inputs(function_name: str) -> dict[str, Any]:
    if function_name == "get_national_average_price":
        return {}
    if function_name == "get_lowest_price_top20":
        return {
            "prodcd": st.selectbox("제품", list(ProductCode), format_func=lambda item: item.value),
            "cnt": st.number_input("건수", min_value=1, max_value=20, value=10),
            "area": st.text_input("지역 코드"),
        }
    if function_name == "search_stations_around":
        coordinate_mode = st.radio("좌표", ["WGS84", "KATEC"], horizontal=True)
        if coordinate_mode == "WGS84":
            lon = st.number_input("경도", value=127.0276, format="%.6f")
            lat = st.number_input("위도", value=37.4979, format="%.6f")
            coordinate = PlaceCoordinate(lon=lon, lat=lat)
            katec = None
        else:
            x = st.number_input("KATEC X", value=314871.8, format="%.4f")
            y = st.number_input("KATEC Y", value=544012.0, format="%.4f")
            coordinate = None
            katec = KatecPoint(x, y)
        return {
            "coordinate": coordinate,
            "katec": katec,
            "radius_m": st.number_input("반경(m)", min_value=1, max_value=5000, value=3000),
            "prodcd": st.selectbox("제품", list(ProductCode), format_func=lambda item: item.value),
            "sort": st.selectbox("정렬", list(SortOrder), format_func=lambda item: item.value),
        }
    if function_name == "get_station_detail":
        return {"uni_id": st.text_input("주유소 ID", value="A0010207")}
    if function_name == "get_area_codes":
        return {"sido": st.text_input("시도 코드")}
    raise ValueError(f"unknown function: {function_name}")


def _run_debug(debug_client: Any, function_name: str, inputs: dict[str, Any]) -> DebugRun:
    if function_name == "get_national_average_price":
        return debug_client.get_national_average_price()
    if function_name == "get_lowest_price_top20":
        return debug_client.get_lowest_price_top20(
            inputs["prodcd"],
            cnt=int(inputs["cnt"]),
            area=inputs["area"] or None,
        )
    if function_name == "search_stations_around":
        return debug_client.search_stations_around(
            coordinate=inputs["coordinate"],
            katec=inputs["katec"],
            radius_m=int(inputs["radius_m"]),
            prodcd=inputs["prodcd"],
            sort=inputs["sort"],
        )
    if function_name == "get_station_detail":
        return debug_client.get_station_detail(inputs["uni_id"])
    if function_name == "get_area_codes":
        return debug_client.get_area_codes(inputs["sido"] or None)
    raise ValueError(f"unknown function: {function_name}")


def _render_fixture_tab(tab: Any, run: DebugRun) -> None:
    with tab:
        case_name = st.text_input("Case name", value=f"{run.function}-case")
        description = st.text_area("Description", value=f"{run.dataset_name} fixture")
        assertion_mode = st.selectbox("Assertion mode", ["snapshot", "schema_only", "required_fields", "count"])
        exclude_fields_raw = st.text_input("Exclude fields", value="fetched_at, request_id, updated_at")
        required_fields_raw = st.text_input("Required fields", value="")
        overwrite = st.checkbox("Overwrite existing fixture", value=False)
        assertion = {
            "mode": assertion_mode,
            "exclude_fields": [value.strip() for value in exclude_fields_raw.split(",") if value.strip()],
            "required_fields": [value.strip() for value in required_fields_raw.split(",") if value.strip()],
        }
        st.json(
            {
                "function": run.function,
                "dataset_name": run.dataset_name,
                "fixture_dir": "tests/fixtures",
                "assertion": assertion,
            }
        )
        if st.button("Save as fixture"):
            try:
                path = save_debug_fixture(
                    base_dir=PROJECT_ROOT / "tests" / "fixtures",
                    debug_run=run,
                    case_name=case_name,
                    description=description,
                    assertion=assertion,
                    overwrite=overwrite,
                )
            except FileExistsError as exc:
                st.error(str(exc))
            else:
                st.success(f"Saved: {path.relative_to(PROJECT_ROOT)}")


if __name__ == "__main__":
    main()
