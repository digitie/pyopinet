"""디버그 UI fixture를 재생하는 pytest runner."""

from __future__ import annotations

from typing import Any

from opinet.debug import SUPPORTED_DEBUG_FUNCTIONS, parse_debug_response, process_debug_result, replay_fixture_case

RUNNERS: dict[str, dict[str, Any]] = {
    function_name: {
        "parse": parse_debug_response,
        "process": process_debug_result,
    }
    for function_name in SUPPORTED_DEBUG_FUNCTIONS
}


def run_fixture_case(case: dict[str, Any]) -> Any:
    """표준 fixture case를 replay하고 assertion을 수행한다."""
    return replay_fixture_case(case)
