"""Tool registry — imports and registers all MCP tools."""

from .api_gateway import register_api_gateway_tools
from .sprints import register_sprint_tools
from .crm import register_crm_tools
from .agents import register_agent_tools
from .platform import register_platform_tools
from .email import register_email_tools
from .analytics import register_analytics_tools
from .temporal import register_temporal_tools


def register_all_tools(app, api_client, enable_temporal: bool = True):
    """Register all tool groups with the MCP app."""
    register_api_gateway_tools(app, api_client)
    register_sprint_tools(app, api_client)
    register_crm_tools(app, api_client)
    register_agent_tools(app, api_client)
    register_platform_tools(app, api_client)
    register_email_tools(app, api_client)
    register_analytics_tools(app, api_client)
    if enable_temporal:
        register_temporal_tools(app)
