"""저장된 디버그 UI fixture를 공통 runner로 replay한다."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from tests.runners import RUNNERS, run_fixture_case

FIXTURE_DIR = Path(__file__).parent / "fixtures"


def _is_debug_fixture(path: Path) -> bool:
    try:
        case = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return False
    return (
        isinstance(case, dict)
        and isinstance(case.get("function"), str)
        and case["function"] in RUNNERS
        and isinstance(case.get("response"), dict)
    )


def all_fixture_files() -> list[Path]:
    """tests/fixtures/{function}/{case}.json 형태의 replay fixture만 찾는다."""
    return sorted(path for path in FIXTURE_DIR.glob("*/*.json") if _is_debug_fixture(path))


@pytest.mark.parametrize(
    "fixture_path",
    all_fixture_files(),
    ids=lambda path: f"{path.parent.name}/{path.stem}",
)
def test_generated_fixtures(fixture_path: Path) -> None:
    with fixture_path.open("r", encoding="utf-8") as handle:
        case: dict[str, Any] = json.load(handle)

    actual = run_fixture_case(case)

    assert actual is not None
