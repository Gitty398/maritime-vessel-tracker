import requests
from django.conf import settings

BASE_URL = "https://api.marinesia.com/api/v1"

def vessels_in_bbox(lat_min, lat_max, lon_min, lon_max):
    params = {
        "key": settings.MARINESIA_API_KEY,
        "lat_min": lat_min,
        "lat_max": lat_max,
        "long_min": lon_min,
        "long_max": lon_max,
    }
    r = requests.get(f"{BASE_URL}/vessel/nearby", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def updated_vessel_location(mmsi):
    params = {
        "key": settings.MARINESIA_API_KEY,
        "mmsi": mmsi,
    }
    r = requests.get(f"{BASE_URL}/vessel/{mmsi}/location/latest", params=params, timeout=30)
    r.raise_for_status()
    return r.json()