import requests
from django.conf import settings

BASE_URL = "https://api.myshiptracking.com/api/v2"


class MyShipTrackingError(Exception):
    def __init__(self, status_code: int, message: str, body: str = ""):
        super().__init__(message)
        self.status_code = status_code
        self.body = body


def _get(path, params=None, timeout=30):
    headers = {
        "Authorization": f"Bearer {settings.MST_API_KEY}",
        "Accept": "application/json",
    }

    r = requests.get(
        f"{BASE_URL}{path}",
        params=params or {},
        headers=headers,
        timeout=timeout,
    )

    # MyShipTracking uses 402 for billing/credits issues
    if r.status_code == 402:
        raise MyShipTrackingError(
            402,
            "MyShipTracking returned 402 (Payment Required). This usually means your API plan has no credits or the endpoint isn’t included.",
            r.text,
        )

    # Auth / permission problems
    if r.status_code in (401, 403):
        raise MyShipTrackingError(
            r.status_code,
            "MyShipTracking authorization failed (check API key / permissions).",
            r.text,
        )

    # Other HTTP errors
    if not r.ok:
        raise MyShipTrackingError(
            r.status_code,
            f"MyShipTracking request failed with HTTP {r.status_code}.",
            r.text,
        )

    return r.json()


def vessels_in_bbox(lat_min, lat_max, lon_min, lon_max):
    params = {
        "minlat": lat_min,
        "maxlat": lat_max,
        "minlon": lon_min,
        "maxlon": lon_max,
    }
    return _get("/vessel/zone", params=params)


def updated_vessel_location(mmsi):
    return _get("/vessel", params={"mmsi": mmsi})