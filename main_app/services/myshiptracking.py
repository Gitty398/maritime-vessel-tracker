import requests
from django.conf import settings

BASE_URL = "https://api.myshiptracking.com/api/v2"



def _get(path, params=None, timeout=30):
    headers = {"Authorization": f"Bearer {settings.MST_API_KEY}"}
    r = requests.get(f"{BASE_URL}{path}", params=params or {}, headers=headers, timeout=timeout)
    r.raise_for_status()
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