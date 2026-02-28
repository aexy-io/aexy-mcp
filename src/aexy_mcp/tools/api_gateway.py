"""Generic API gateway tool — 100% API coverage escape hatch."""

from __future__ import annotations

import json
from typing import Any


def register_api_gateway_tools(app, api_client):
    """Register the generic aexy_api tool."""

    @app.tool(
        name="aexy_api",
        description=(
            "Call any Aexy API endpoint directly. Use this for endpoints not covered "
            "by dedicated tools, or when you need full control over the request. "
            "The base URL already points to /api/v1, so paths should be relative "
            "(e.g., '/health', '/developers/me', '/workspaces/{id}/teams')."
        ),
    )
    async def aexy_api(
        method: str,
        path: str,
        body: dict[str, Any] | None = None,
        query_params: dict[str, Any] | None = None,
    ) -> str:
        """Call any Aexy API endpoint.

        Args:
            method: HTTP method (GET, POST, PUT, PATCH, DELETE)
            path: API path relative to /api/v1 (e.g., '/health', '/developers/me')
            body: Request body for POST/PUT/PATCH requests
            query_params: URL query parameters
        """
        result = await api_client.request(method, path, body=body, params=query_params)
        return json.dumps(result, indent=2, default=str)
