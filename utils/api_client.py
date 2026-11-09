"""
Reusable HTTP API Client built on top of Requests Session.
Provides centralized logging, authentication handling, timing, and error handling.
"""

import json
from typing import Any, Dict, Optional
import requests
from requests import Response

from config.config import settings
from utils.logger import get_logger

logger = get_logger("APIClient")


class APIClient:
    """
    HTTP Client wrapper around requests.Session for REST API automation.
    Enforces consistent base URL, timeouts, headers, logging, and response timing.
    """

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[float] = None) -> None:
        self.base_url: str = (base_url or settings.BASE_URL).rstrip("/")
        self.timeout: float = timeout or settings.DEFAULT_TIMEOUT
        self.session: requests.Session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Python-API-Automation-Framework/1.0"
        })

    def set_bearer_token(self, token: str) -> None:
        """Set Bearer authentication token for all subsequent requests."""
        self.session.headers["Authorization"] = f"Bearer {token}"
        logger.debug("Bearer token configured on APIClient session.")

    def clear_bearer_token(self) -> None:
        """Remove Authorization header from session."""
        self.session.headers.pop("Authorization", None)
        logger.debug("Bearer token removed from APIClient session.")

    def _build_url(self, endpoint: str) -> str:
        """Construct full absolute URL from endpoint."""
        if endpoint.startswith("http://") or endpoint.startswith("https://"):
            return endpoint
        clean_endpoint = endpoint.lstrip("/")
        return f"{self.base_url}/{clean_endpoint}"

    def _log_request(
        self,
        method: str,
        url: str,
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Any] = None
    ) -> None:
        """Format and log outgoing HTTP request details."""
        logger.info(f"===> REQUEST: {method.upper()} {url}")
        if params:
            logger.debug(f"Params: {params}")
        if headers:
            logger.debug(f"Headers: {headers}")
        if json_data is not None:
            logger.debug(f"Payload: {json.dumps(json_data, indent=2)}")

    def _log_response(self, response: Response) -> None:
        """Format and log incoming HTTP response details."""
        elapsed_ms = response.elapsed.total_seconds() * 1000
        logger.info(
            f"<=== RESPONSE: {response.status_code} {response.reason} "
            f"in {elapsed_ms:.2f}ms [{response.url}]"
        )
        try:
            body = response.json()
            logger.debug(f"Response Body: {json.dumps(body, indent=2)}")
        except Exception:
            logger.debug(f"Response Text: {response.text[:500]}")

    def request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
        headers: Optional[Dict[str, str]] = None,
        timeout: Optional[float] = None,
        **kwargs: Any
    ) -> Response:
        """
        Execute an HTTP request with automatic logging, timing, and error tracking.
        """
        url = self._build_url(endpoint)
        request_timeout = timeout if timeout is not None else self.timeout

        self._log_request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json_data=json
        )

        try:
            response = self.session.request(
                method=method.upper(),
                url=url,
                params=params,
                json=json,
                data=data,
                headers=headers,
                timeout=request_timeout,
                **kwargs
            )
            # Attach measured elapsed time in milliseconds directly to the response object
            response.elapsed_ms = response.elapsed.total_seconds() * 1000  # type: ignore[attr-defined]

            self._log_response(response)
            return response

        except requests.RequestException as exc:
            logger.error(f"HTTP Request Failed: {method.upper()} {url} - Error: {str(exc)}")
            raise

    def get(self, endpoint: str, **kwargs: Any) -> Response:
        """Send HTTP GET request."""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint: str, **kwargs: Any) -> Response:
        """Send HTTP POST request."""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint: str, **kwargs: Any) -> Response:
        """Send HTTP PUT request."""
        return self.request("PUT", endpoint, **kwargs)

    def patch(self, endpoint: str, **kwargs: Any) -> Response:
        """Send HTTP PATCH request."""
        return self.request("PATCH", endpoint, **kwargs)

    def delete(self, endpoint: str, **kwargs: Any) -> Response:
        """Send HTTP DELETE request."""
        return self.request("DELETE", endpoint, **kwargs)

