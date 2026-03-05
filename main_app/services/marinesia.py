# services/marinesia.py
from dataclasses import dataclass
from typing import Any, Dict, Optional
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class MarinesiaError(Exception):
    pass


@dataclass(frozen=True)
class MarinesiaClient:
    api_key: str
    base_url: str = "https://api.marinesia.com"
    connect_timeout: float = 5.0
    read_timeout: float = 30.0

    def _session(self) -> requests.Session:
        s = requests.Session()
        retries = Retry(
            total=4,
            backoff_factor=0.6,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
            raise_on_status=False,
        )
        s.mount("https://", HTTPAdapter(max_retries=retries))
        return s

    def _get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        params = dict(params or {})
        params["key"] = self.api_key

        url = f"{self.base_url}{path}"
        try:
            r = self._session().get(url, params=params, timeout=(self.connect_timeout, self.read_timeout))
        except requests.Timeout as e:
            raise MarinesiaError(f"Marinesia timed out (connect={self.connect_timeout}s, read={self.read_timeout}s).") from e
        except requests.RequestException as e:
            raise MarinesiaError(f"Network error calling Marinesia: {e}") from e

        if r.status_code == 429:
            raise MarinesiaError("Marinesia rate limit exceeded (429).")
        if r.status_code >= 400:
            raise MarinesiaError(f"Marinesia HTTP {r.status_code}: {r.text[:200]}")

        try:
            payload = r.json()
        except ValueError as e:
            raise MarinesiaError("Marinesia returned non-JSON response.") from e

        if payload.get("error") is True:
            raise MarinesiaError(payload.get("message") or "Marinesia error")

        return payload