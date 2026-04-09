from typing import Any

import httpx

from app.core.exceptions import IngestionError


class HTTPIngestionClient:
    def __init__(
        self,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.headers = headers or {}
        self.timeout = timeout

    def _build_url(self, endpoint: str | None = None, absolute_url: str | None = None) -> str:
        if absolute_url:
            return absolute_url
        if self.base_url and endpoint:
            return f"{self.base_url}/{endpoint.lstrip('/')}"
        raise IngestionError("A valid absolute_url or endpoint + base_url is required.")

    def get_bytes(
        self,
        endpoint: str | None = None,
        absolute_url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> bytes:
        url = self._build_url(endpoint=endpoint, absolute_url=absolute_url)
        merged_headers = {**self.headers, **(headers or {})}
        try:
            response = httpx.get(url, params=params, headers=merged_headers, timeout=self.timeout)
            response.raise_for_status()
        except httpx.HTTPError as exc:
            raise IngestionError(f"HTTP ingestion failed for {url}: {exc}") from exc
        return response.content

    def get_json(
        self,
        endpoint: str | None = None,
        absolute_url: str | None = None,
        params: dict[str, Any] | None = None,
        headers: dict[str, str] | None = None,
    ) -> Any:
        url = self._build_url(endpoint=endpoint, absolute_url=absolute_url)
        merged_headers = {**self.headers, **(headers or {})}
        try:
            response = httpx.get(url, params=params, headers=merged_headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as exc:
            raise IngestionError(f"HTTP ingestion failed for {url}: {exc}") from exc
        except ValueError as exc:
            raise IngestionError(f"Invalid JSON response for {url}") from exc
