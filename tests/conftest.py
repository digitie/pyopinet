"""Shared pytest helpers for Opinet tests."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from opinet import OpinetClient

OPINET_BASE_URL = "https://www.opinet.co.kr/api/"


@pytest.fixture
def load_fixture() -> Any:
    def _load(name: str) -> Any:
        path = Path(__file__).parent / "fixtures" / name
        with path.open(encoding="utf-8") as handle:
            return json.load(handle)

    return _load


@pytest.fixture
def client() -> OpinetClient:
    return OpinetClient(api_key="test-key", retry_backoff=0)
