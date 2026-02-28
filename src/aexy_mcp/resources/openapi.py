"""MCP resources — OpenAPI spec, Temporal activity config, schedules."""

from __future__ import annotations

import json

from ..temporal_client import get_temporal_client


# Hardcoded from backend/src/aexy/temporal/task_queues.py
TASK_QUEUES = {
    "ANALYSIS": "analysis",
    "SYNC": "sync",
    "WORKFLOWS": "workflows",
    "EMAIL": "email",
    "INTEGRATIONS": "integrations",
    "OPERATIONS": "operations",
}


def register_resources(app, api_client, enable_temporal: bool = True):
    """Register MCP resources."""

    @app.resource(
        uri="aexy://openapi-spec",
        name="Aexy OpenAPI Spec",
        description="Full OpenAPI specification for the Aexy API. Use this to discover all available endpoints.",
    )
    async def get_openapi_spec() -> str:
        """Fetch the OpenAPI spec from the running Aexy backend."""
        # The spec is at /openapi.json relative to the API root
        # api_client base URL is /api/v1, so we go up to root
        import httpx
        from ..config import config

        # Build root URL from API URL (strip /api/v1)
        root_url = config.api_url.rstrip("/")
        if root_url.endswith("/api/v1"):
            root_url = root_url[:-7]

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(f"{root_url}/openapi.json")
            return response.text

    @app.resource(
        uri="aexy://task-queues",
        name="Temporal Task Queues",
        description="All 6 Temporal task queue definitions used for routing activities.",
    )
    async def get_task_queues() -> str:
        """Return task queue definitions."""
        return json.dumps(TASK_QUEUES, indent=2)

    if enable_temporal:
        @app.resource(
            uri="aexy://temporal/schedules",
            name="Temporal Schedules",
            description="All registered Temporal schedules with intervals and next run times.",
        )
        async def get_schedules_resource() -> str:
            """Fetch live schedule data from Temporal."""
            try:
                client = await get_temporal_client()
                schedules = []
                async for schedule in client.list_schedules():
                    info = schedule.info
                    entry = {
                        "id": schedule.id,
                        "paused": info.paused if info else False,
                    }
                    if info and info.next_action_times:
                        entry["next_run"] = info.next_action_times[0].isoformat()
                    if info and info.num_actions:
                        entry["total_runs"] = info.num_actions
                    schedules.append(entry)
                return json.dumps(schedules, indent=2, default=str)
            except Exception as e:
                return json.dumps({"error": f"Could not connect to Temporal: {e}"})
