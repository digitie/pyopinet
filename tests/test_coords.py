import pytest

from opinet.coords import katec_to_wgs84, wgs84_to_katec


@pytest.mark.parametrize(
    ("lon", "lat"),
    [
        (127.0276, 37.4979),
        (126.9784, 37.5666),
        (129.0756, 35.1796),
    ],
)
def test_roundtrip(lon, lat):
    x, y = wgs84_to_katec(lon, lat)
    lon2, lat2 = katec_to_wgs84(x, y)
    assert abs(lon2 - lon) < 1e-5
    assert abs(lat2 - lat) < 1e-5


@pytest.mark.parametrize(
    ("katec", "lon_range", "lat_range"),
    [
        ((314871.80, 544012.00), (127.02, 127.06), (37.49, 37.51)),
        ((392585.72, 485368.43), (127.91, 127.94), (36.96, 37.00)),
        ((430907.88, 392046.93), (128.32, 128.36), (36.10, 36.14)),
    ],
)
def test_real_station_coords(katec, lon_range, lat_range):
    lon, lat = katec_to_wgs84(*katec)
    assert lon_range[0] < lon < lon_range[1]
    assert lat_range[0] < lat < lat_range[1]


def test_invalid_input():
    with pytest.raises(ValueError):
        wgs84_to_katec(float("nan"), 37.5)
    with pytest.raises(ValueError):
        katec_to_wgs84(float("inf"), 540000)
