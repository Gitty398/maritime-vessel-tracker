import requests
from dataclasses import dataclass
from django.conf import settings

BASE_URL = "https://api.marinesia.com/api/v1"


@dataclass(frozen=True)
class MarinesiaError(Exception):
    message: str
    status_code: int = 502

    def __str__(self):
        return self.message


def _get(path: str, params: dict, timeout=(5, 20)) -> dict:
    if not settings.MARINESIA_API_KEY:
        raise MarinesiaError("MARINESIA_API_KEY is not set.", 500)

    p = dict(params)
    p["key"] = settings.MARINESIA_API_KEY
    url = f"{BASE_URL}{path}"

    try:
        resp = requests.get(url, params=p, timeout=timeout)
    except requests.Timeout as e:
        raise MarinesiaError(
            "Marinesia API timed out. Please try again.",
            504,
        ) from e
    except requests.RequestException as e:
        raise MarinesiaError(f"Could not reach Marinesia API: {e}", 502) from e

    if resp.status_code >= 400:
        try:
            payload = resp.json()
            msg = payload.get("message") or payload.get("detail") or resp.text
        except Exception:
            msg = resp.text
        raise MarinesiaError(msg, resp.status_code)

    try:
        return resp.json()
    except ValueError as e:
        raise MarinesiaError("Marinesia returned invalid JSON.", 502) from e


def vessels_nearby_bbox(lat_min, lat_max, lon_min, lon_max):
    return _get(
        "/vessel/nearby",
        {
            "lat_min": lat_min,
            "lat_max": lat_max,
            "long_min": lon_min,
            "long_max": lon_max,
        },
    )


def latest_location_by_mmsi(mmsi):
    return _get(f"/vessel/{mmsi}/location/latest", {}, timeout=(5, 40))