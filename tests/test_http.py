import requests
import responses
import pytest

from opinet import OpinetClient
from opinet.exceptions import OpinetAuthError, OpinetNetworkError, OpinetRateLimitError, OpinetServerError

OPINET_BASE_URL = "https://www.opinet.co.kr/api/"


@responses.activate
def test_invalid_key_body_maps_to_auth(load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", json=load_fixture("error_invalid_key.json"))
    client = OpinetClient(api_key="bad-key", retry_backoff=0)

    with pytest.raises(OpinetAuthError):
        client.get_national_average_price()


@responses.activate
def test_limit_body_maps_to_rate_limit(load_fixture):
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", json=load_fixture("error_rate_limit.json"))
    client = OpinetClient(api_key="test-key", retry_backoff=0)

    with pytest.raises(OpinetRateLimitError):
        client.get_national_average_price()


@responses.activate
def test_401_and_403_map_to_auth():
    for status in (401, 403):
        responses.reset()
        responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", body="no", status=status)
        client = OpinetClient(api_key="test-key", retry_backoff=0)
        with pytest.raises(OpinetAuthError):
            client.get_national_average_price()


@responses.activate
def test_429_does_not_retry():
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", body="limit", status=429)
    client = OpinetClient(api_key="test-key", retry_backoff=0, max_retries=2)

    with pytest.raises(OpinetRateLimitError):
        client.get_national_average_price()
    assert len(responses.calls) == 1


@responses.activate
def test_5xx_retries_then_succeeds(load_fixture):
    url = OPINET_BASE_URL + "avgAllPrice.do"
    responses.add(responses.GET, url, body="server down", status=500)
    responses.add(responses.GET, url, body="still down", status=502)
    responses.add(responses.GET, url, json=load_fixture("avg_all_price.json"), status=200)
    client = OpinetClient(api_key="test-key", retry_backoff=0, max_retries=2)

    rows = client.get_national_average_price()

    assert len(responses.calls) == 3
    assert rows[0].product_name == "고급휘발유"


@responses.activate
def test_5xx_final_failure():
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", body="server down", status=500)
    client = OpinetClient(api_key="test-key", retry_backoff=0, max_retries=0)

    with pytest.raises(OpinetServerError):
        client.get_national_average_price()


@responses.activate
def test_network_error_retries_then_raises():
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", body=requests.ConnectionError("offline"))
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", body=requests.Timeout("slow"))
    client = OpinetClient(api_key="test-key", retry_backoff=0, max_retries=1)

    with pytest.raises(OpinetNetworkError):
        client.get_national_average_price()
    assert len(responses.calls) == 2


@responses.activate
def test_json_parse_failure_maps_to_server_error():
    responses.add(responses.GET, OPINET_BASE_URL + "avgAllPrice.do", body="not json", content_type="text/plain")
    client = OpinetClient(api_key="test-key", retry_backoff=0)

    with pytest.raises(OpinetServerError):
        client.get_national_average_price()
