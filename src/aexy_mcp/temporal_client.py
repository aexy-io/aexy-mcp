"""Temporal SDK client for workflow debugging."""

from __future__ import annotations

from temporalio.client import Client

from .config import config

_client: Client | None = None


async def get_temporal_client() -> Client:
    """Get or create the Temporal client singleton."""
    global _client
    if _client is None:
        _client = await Client.connect(
            config.temporal_address,
            namespace=config.temporal_namespace,
        )
    return _client
