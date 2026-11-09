"""
Reusable HTTP API Client wrapper around requests.Session.
"""
import time
import requests

class APIClient:
    def __init__(self, base_url: str, timeout: float = 10.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({"Accept": "application/json"})

    def request(self, method: str, path: str, **kwargs) -> requests.Response:
        url = path if path.startswith("http") else f"{self.base_url}/{path.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)
        start = time.perf_counter()
        resp = self.session.request(method.upper(), url, **kwargs)
        resp.elapsed_ms = (time.perf_counter() - start) * 1000
        return resp

    def get(self, path: str, **kwargs): return self.request("GET", path, **kwargs)
    def post(self, path: str, **kwargs): return self.request("POST", path, **kwargs)
    def put(self, path: str, **kwargs): return self.request("PUT", path, **kwargs)
    def patch(self, path: str, **kwargs): return self.request("PATCH", path, **kwargs)
    def delete(self, path: str, **kwargs): return self.request("DELETE", path, **kwargs)
