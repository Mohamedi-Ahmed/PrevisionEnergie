import time
from typing import Any

import httpx

from app.core.exceptions import IngestionError


class HTTPIngestionClient:
    def __init__(
        self,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.headers = headers or {}
        self.timeout = timeout
        self.max_retries = max_retries
        self.backoff_seconds = backoff_seconds

    def _build_url(self, endpoint: str | None = None, absolute_url: str | None = None) -> str:
        if absolute_url:
            return absolute_url
        if self.base_url and endpoint:
            return f"{self.base_url}/{endpoint.lstrip('/')}"
        raise IngestionError("A valid absolute_url or endpoint + base_url is required.")

    def _request(
        self,
        *,
        endpoint: str | None = None,
        absolute_url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        url = self._build_url(endpoint=endpoint, absolute_url=absolute_url)
        merged_headers = {**self.headers, **(headers or {})}
        last_error: httpx.HTTPError | None = None
        for attempt in range(self.max_retries + 1):
            try:
                response = httpx.get(url, params=params, headers=merged_headers, timeout=self.timeout)
                response.raise_for_status()
                return response
            except httpx.HTTPError as exc:
                last_error = exc
                if attempt >= self.max_retries:
                    break
                time.sleep(self.backoff_seconds * (2 ** attempt))
        raise IngestionError(f"HTTP ingestion failed for {url}: {last_error}") from last_error

    def get_bytes(
        self,
        endpoint: str | None = None,
        absolute_url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        response = self._request(
            endpoint=endpoint,
            absolute_url=absolute_url,
            params=params,
            headers=headers,
        )
        return response.content

    def get_json(
        self,
        endpoint: str | None = None,
        absolute_url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        response = self._request(
            endpoint=endpoint,
            absolute_url=absolute_url,
            params=params,
            headers=headers,
        )
        try:
            return response.json()
        except ValueError as exc:
            url = self._build_url(endpoint=endpoint, absolute_url=absolute_url)
            raise IngestionError(f"Invalid JSON response for {url}") from exc
