import requests
from django.conf import settings

BASE_URL = "https://api.marinesia.com/api/v1"


class MarinesiaError(Exception):
    """Raised when a Marinesia API request fails."""


def _get(path: str, params: dict, *, timeout: int = 12):
    api_key = settings.MARINESIA_API_KEY
    if not api_key:
        raise MarinesiaError("MARINESIA_API_KEY is not set.")

    params = {"key": api_key, **params}

    try:
        r = requests.get(f"{BASE_URL}{path}", params=params, timeout=timeout)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise MarinesiaError(str(e)) from e


def vessels_in_bbox(lat_min, lat_max, lon_min, lon_max):
    return _get(
        "/vessel/nearby",
        {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "long_min": lon_min,
            "long_max": lon_max,
        },
    )


def latest_location_by_mmsi(mmsi: int):
    return _get("/vessel/latest", {"mmsi": mmsi})