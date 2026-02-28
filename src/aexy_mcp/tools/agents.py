"""AI agent and workflow tools."""

from __future__ import annotations

import json
from typing import Any


def register_agent_tools(app, api_client):
    """Register agent and workflow tools."""

    @app.tool(
        name="aexy_agents",
        description=(
            "Manage AI agents. Actions: list, get, create, update, delete, execute, "
            "list_conversations, get_conversation, get_metrics, list_executions."
        ),
    )
    async def aexy_agents(
        action: str,
        workspace_id: str,
        agent_id: str | None = None,
        conversation_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage AI agents.

        Args:
            action: list, get, create, update, delete, execute, list_conversations, get_conversation, get_metrics, list_executions
            workspace_id: Workspace ID
            agent_id: Agent ID (required for most actions)
            conversation_id: Conversation ID (for get_conversation)
            data: Request body for create/update/execute
            params: Query parameters
        """
        base = f"/workspaces/{workspace_id}/crm/agents"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{agent_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{agent_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{agent_id}")
            case "execute":
                result = await api_client.post(f"{base}/{agent_id}/execute", body=data)
            case "list_conversations":
                result = await api_client.get(f"{base}/{agent_id}/conversations", params=params)
            case "get_conversation":
                result = await api_client.get(f"{base}/{agent_id}/conversations/{conversation_id}")
            case "get_metrics":
                result = await api_client.get(f"{base}/{agent_id}/metrics")
            case "list_executions":
                result = await api_client.get(f"{base}/{agent_id}/executions", params=params)
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, execute, list_conversations, get_conversation, get_metrics, list_executions"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_agent_policies",
        description=(
            "Manage agent policies and audit logs. "
            "Actions: list, get, create, update, delete, policy_decisions, config_audit."
        ),
    )
    async def aexy_agent_policies(
        action: str,
        workspace_id: str,
        policy_id: str | None = None,
        agent_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage agent policies.

        Args:
            action: list, get, create, update, delete, policy_decisions, config_audit
            workspace_id: Workspace ID
            policy_id: Policy ID (for get, update, delete)
            agent_id: Agent ID (for policy_decisions, config_audit)
            data: Request body for create/update
        """
        base = f"/workspaces/{workspace_id}/crm/agent-policies"

        match action:
            case "list":
                result = await api_client.get(base)
            case "get":
                result = await api_client.get(f"{base}/{policy_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{policy_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{policy_id}")
            case "policy_decisions":
                result = await api_client.get(
                    f"/workspaces/{workspace_id}/crm/agents/{agent_id}/policy-decisions"
                )
            case "config_audit":
                result = await api_client.get(
                    f"/workspaces/{workspace_id}/crm/agents/{agent_id}/config-audit"
                )
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, policy_decisions, config_audit"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_workflows",
        description=(
            "Manage CRM automation workflows (visual workflow builder). "
            "Actions: get, update, validate, publish, list_executions, get_execution."
        ),
    )
    async def aexy_workflows(
        action: str,
        workspace_id: str,
        automation_id: str,
        execution_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage CRM automation workflows.

        Args:
            action: get, update, validate, publish, list_executions, get_execution
            workspace_id: Workspace ID
            automation_id: Automation ID that owns the workflow
            execution_id: Execution ID (for get_execution)
            data: Request body for update
        """
        base = f"/workspaces/{workspace_id}/crm/automations/{automation_id}/workflow"

        match action:
            case "get":
                result = await api_client.get(base)
            case "update":
                result = await api_client.put(base, body=data)
            case "validate":
                result = await api_client.post(f"{base}/validate")
            case "publish":
                result = await api_client.post(f"{base}/publish")
            case "list_executions":
                result = await api_client.get(f"{base}/executions")
            case "get_execution":
                result = await api_client.get(f"{base}/executions/{execution_id}")
            case _:
                return f"Unknown action: {action}. Valid: get, update, validate, publish, list_executions, get_execution"

        return json.dumps(result, indent=2, default=str)
