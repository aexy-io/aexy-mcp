"""MCP resources — read-only context for Claude."""

from .openapi import register_resources


def register_all_resources(app, api_client, enable_temporal: bool = True):
    """Register all MCP resources."""
    register_resources(app, api_client, enable_temporal)
