"""Aexy MCP Server — entry point."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from .api_client import AexyAPIClient
from .config import config
from .tools import register_all_tools
from .resources import register_all_resources
from .prompts import register_all_prompts

app = FastMCP(
    "aexy",
    instructions=(
        "MCP server for the Aexy Engineering OS platform. "
        "Provides tools for sprint management, CRM, AI agents, email marketing, "
        "analytics, and Temporal workflow debugging."
    ),
)

# Initialize shared API client
api_client = AexyAPIClient(base_url=config.api_url, token=config.api_token)

# Register all components
register_all_tools(app, api_client, enable_temporal=config.enable_temporal)
register_all_resources(app, api_client, enable_temporal=config.enable_temporal)
register_all_prompts(app, enable_temporal=config.enable_temporal)


def main():
    """Run the MCP server via stdio transport."""
    app.run(transport="stdio")


if __name__ == "__main__":
    main()
