"""Async HTTP client for the Aexy backend API."""

from __future__ import annotations

import json
from typing import Any

import httpx

from .config import config


class AexyAPIClient:
    """Thin httpx wrapper with JWT Bearer auth."""

    def __init__(self, base_url: str | None = None, token: str | None = None):
        self._base_url = base_url or config.api_url
        self._token = token or config.api_token
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self._base_url,
                headers={"Authorization": f"Bearer {self._token}"},
                timeout=30.0,
            )
        return self._client

    async def request(
        self,
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[Any] | str:
        """Make an authenticated API request."""
        client = await self._get_client()

        # Clean params: remove None values
        if params:
            params = {k: v for k, v in params.items() if v is not None}

        response = await client.request(
            method=method.upper(),
            url=path,
            json=body,
            params=params,
        )

        # Try to parse as JSON, fall back to text
        try:
            return response.json()
        except (json.JSONDecodeError, ValueError):
            return {"status_code": response.status_code, "text": response.text}

    async def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        return await self.request("GET", path, params=params)

    async def post(self, path: str, body: dict[str, Any] | None = None, params: dict[str, Any] | None = None) -> Any:
        return await self.request("POST", path, body=body, params=params)

    async def put(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return await self.request("PUT", path, body=body)

    async def patch(self, path: str, body: dict[str, Any] | None = None) -> Any:
        return await self.request("PATCH", path, body=body)

    async def delete(self, path: str) -> Any:
        return await self.request("DELETE", path)

    async def close(self):
        if self._client:
            await self._client.aclose()
            self._client = None


# Module-level singleton
api_client = AexyAPIClient()
