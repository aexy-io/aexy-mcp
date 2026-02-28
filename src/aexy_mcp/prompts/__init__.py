"""MCP prompts — pre-built conversation starters."""

from .workflows import register_prompts


def register_all_prompts(app, enable_temporal: bool = True):
    """Register all MCP prompts."""
    register_prompts(app, enable_temporal)
