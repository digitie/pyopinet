# pyopinet Implementation Status

이 문서는 현재 구현 상태, 검증 방법, 다음 작업자가 반복하지 말아야 할 판단을 한곳에 모읍니다.

## 현재 범위

`OpinetClient`는 오피넷 공식 오픈 API 페이지에 등재된 5개 엔드포인트만 안정 구현 대상으로 둡니다.

| Method | Endpoint | Status | Notes |
|---|---|---|---|
| `get_national_average_price()` | `avgAllPrice.do` | Implemented | `TRADE_DT`, `PRICE`, `DIFF`를 Python 타입으로 변환 |
| `get_lowest_price_top20()` | `lowTop10.do` | Implemented | `cnt` 1~20, `area` 2/4자리 사전 검증 |
| `search_stations_around()` | `aroundAll.do` | Implemented | WGS84 입력은 KATEC으로 변환 후 요청 |
| `get_station_detail()` | `detailById.do` | Implemented | `LPG_YN`은 `StationType`, `KPETRO_YN`은 `is_kpetro` |
| `get_area_codes()` | `areaCode.do` | Implemented | 코드값은 선행 0 보존을 위해 항상 `str` |

PDF 가이드북의 추가 API는 아직 공식 명세 페이지가 없으므로 `opinet.experimental`에 둡니다. 검증 전에는 안정 API로 승격하지 않습니다.

## 구현 원칙

- 인증 파라미터는 `certkey`, 출력 포맷은 `out=json`입니다.
- HTTP 상태/본문 기반 오류 매핑은 `opinet/_http.py`에 모읍니다.
- 엔드포인트 파라미터 오류는 HTTP 호출 전에 `OpinetInvalidParameterError`로 실패시킵니다.
- API 응답은 모델 생성 전에 `date`, `time`, `float`, `bool`, `StrEnum`으로 변환합니다.
- `AREA_CD`, `SIGUNCD`, `UNI_ID`, 제품 코드, 상표 코드는 정수로 변환하지 않습니다.
- KATEC 변환은 `opinet/coords.py`의 `pyproj` transformer만 사용합니다.

## 테스트 매트릭스

기본 테스트는 네트워크 없이 실행됩니다.

| Area | Files | Coverage Intent |
|---|---|---|
| Type conversion | `tests/test_convert.py` | 날짜/시간/숫자/불리언/공백 처리 |
| Code mappings | `tests/test_codes.py` | Opinet ↔ BJD 시도 매핑, 알뜰 상표 판정 |
| Coordinates | `tests/test_coords.py` | WGS84↔KATEC 왕복, 실제 주유소 KATEC 권역 |
| HTTP errors | `tests/test_http.py` | 인증/쿼터/5xx/네트워크/JSON 오류 |
| Endpoints | `tests/test_client_endpoints.py` | 공식 5개 API의 타입, 파라미터, 빈 결과, 단일 dict 응답 |
| Experimental boundary | `tests/test_experimental.py` | 미검증 API가 명시적으로 unimplemented임을 고정 |

필수 검증 명령:

```bash
python -m compileall opinet tests
python -m pytest
python -m pytest --cov=opinet --cov-fail-under=90
python -m mypy opinet
```

## Live API 테스트 정책

실제 오피넷 호출은 기본 테스트에 넣지 않습니다.

- `OPINET_API_KEY`가 있을 때만 동작하게 합니다.
- 테스트에는 `@pytest.mark.live`를 붙입니다.
- 캡처한 fixture에는 키, 개인 식별 정보, 호출 URL의 인증 파라미터를 남기지 않습니다.
- 라이브 호출로 확인한 응답도 fixture에 저장할 때 숫자/날짜/시간 필드는 문자열 그대로 둡니다.
- `.env`는 로컬 전용이며 커밋하지 않습니다. `.env.example`만 추적합니다.
- `areaCode.do`처럼 항상 데이터가 있어야 할 엔드포인트가 빈 `RESULT.OIL`을 반환하면 키가 공식 open API 게이트웨이에 provision되지 않은 상태로 간주하고 파싱 smoke 테스트를 skip합니다.

라이브 테스트 실행:

```bash
pytest -m live --run-live
```

### 2026-05-01 Live Run Note

로컬 `.env`의 키로 실제 서버에 연결했을 때 `areaCode.do`의 JSON envelope는 정상 수신되었습니다. 다만 공식 5개 API가 모두 HTTP 200과 빈 `RESULT.OIL`을 반환하는 상태가 관찰되었습니다. 이 응답은 파서 오류가 아니라 키가 공식 open API 게이트웨이에 데이터 반환 권한으로 provision되지 않은 상태일 가능성이 높습니다.

그래서 live 테스트는 두 단계로 나뉩니다.

- 서버 연결과 `RESULT.OIL` envelope 확인은 pass/fail로 검증합니다.
- 실제 데이터 파싱 smoke는 `areaCode.do`가 비어 있으면 skip하고, 데이터가 반환되는 키에서는 공식 5개 API 전체를 검증합니다.

## 반복 실수 방지

이미 한 번 확인한 혼동 지점입니다.

- `StationDetail.tel`을 사용합니다. `phone` 필드를 새로 만들지 않습니다.
- `OilPrice`에는 `product_name`이 없습니다. `OIL_PRICE` 응답에는 `PRODNM`이 오지 않습니다.
- `RESULT.OIL`과 `OIL_PRICE`는 list뿐 아니라 단일 dict로 올 수 있습니다.
- 실제 응답의 상표 필드는 `POLL_DIV_CO`, `GPOLL_DIV_CO`가 우선입니다. `*_CD`는 fallback입니다.
- 공백 1자(`" "`)는 의미 있는 문자열이 아니라 `None`입니다.
- 좌표 테스트 범위는 주소 권역 검증용입니다. 소수점 범위를 너무 좁히면 `pyproj` 버전/환경 차이로 불필요하게 깨질 수 있습니다.
- `types-requests`는 `mypy`용 개발 의존성입니다. 제거하면 타입 검사가 실패합니다.

## 다음 작업 기준

새 엔드포인트를 추가할 때:

1. `opinet-api.md` 또는 실제 응답으로 필드를 확인합니다.
2. 공식 5개에 속하지 않으면 `opinet.experimental`에 둡니다.
3. 모델 필드는 Python 네이티브 타입으로 정의합니다.
4. fixture는 실제 응답처럼 문자열 값을 유지합니다.
5. happy path, empty result, error response, 파라미터 검증 테스트를 추가합니다.
6. README와 이 문서를 갱신합니다.
