import requests
from dataclasses import dataclass
from django.conf import settings

BASE_URL = "https://api.marinesia.com/api/v1"


@dataclass(frozen=True)
class MarinesiaError(Exception):
    message: str
    status_code: int = 502


def _get(path: str, params: dict, timeout: int = 12) -> dict:
    if not settings.MARINESIA_API_KEY:
        raise MarinesiaError("MARINESIA_API_KEY is not set", 500)

    p = dict(params)
    p["key"] = settings.MARINESIA_API_KEY

    url = f"{BASE_URL}{path}"
    resp = requests.get(url, params=p, timeout=timeout)

    if resp.status_code >= 400:
        try:
            payload = resp.json()
            msg = payload.get("message") or payload.get("detail") or resp.text
        except Exception:
            msg = resp.text
        raise MarinesiaError(msg, resp.status_code)

    return resp.json()


def vessels_nearby_bbox(lat_min: float, lat_max: float, lon_min: float, lon_max: float) -> dict:
    return _get(
        "/vessel/nearby",
        {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "long_min": lon_min,
            "long_max": lon_max,
        },
    )