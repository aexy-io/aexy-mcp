"""Platform tools — workspaces, notifications, documents, tickets, tables, integrations."""

from __future__ import annotations

import json
from typing import Any


def register_platform_tools(app, api_client):
    """Register platform-related tools."""

    @app.tool(
        name="aexy_workspaces",
        description=(
            "Manage workspaces. Actions: list, get, get_my, create, update, "
            "members, get_member, teams, permissions."
        ),
    )
    async def aexy_workspaces(
        action: str,
        workspace_id: str | None = None,
        member_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage workspaces.

        Args:
            action: list, get, get_my, create, update, members, get_member, teams, permissions
            workspace_id: Workspace ID (required for most actions)
            member_id: Member ID (for get_member)
            data: Request body for create/update
        """
        match action:
            case "list":
                result = await api_client.get("/workspaces")
            case "get":
                result = await api_client.get(f"/workspaces/{workspace_id}")
            case "get_my":
                result = await api_client.get("/workspaces")
            case "create":
                result = await api_client.post("/workspaces", body=data)
            case "update":
                result = await api_client.patch(f"/workspaces/{workspace_id}", body=data)
            case "members":
                result = await api_client.get(f"/workspaces/{workspace_id}/members")
            case "get_member":
                result = await api_client.get(f"/workspaces/{workspace_id}/members/{member_id}")
            case "teams":
                result = await api_client.get(f"/workspaces/{workspace_id}/teams")
            case "permissions":
                result = await api_client.get(f"/workspaces/{workspace_id}/permissions")
            case _:
                return f"Unknown action: {action}. Valid: list, get, get_my, create, update, members, get_member, teams, permissions"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_notifications",
        description=(
            "Manage notifications. Actions: list, get, count, poll, mark_read, "
            "mark_all_read, delete, get_preferences, update_preference."
        ),
    )
    async def aexy_notifications(
        action: str,
        notification_id: str | None = None,
        event_type: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage notifications.

        Args:
            action: list, get, count, poll, mark_read, mark_all_read, delete, get_preferences, update_preference
            notification_id: Notification ID (for get, mark_read, delete)
            event_type: Event type string (for update_preference)
            data: Request body for update_preference
            params: Query parameters for list
        """
        match action:
            case "list":
                result = await api_client.get("/notifications", params=params)
            case "get":
                result = await api_client.get(f"/notifications/{notification_id}")
            case "count":
                result = await api_client.get("/notifications/count")
            case "poll":
                result = await api_client.get("/notifications/poll")
            case "mark_read":
                result = await api_client.post(f"/notifications/{notification_id}/read")
            case "mark_all_read":
                result = await api_client.post("/notifications/read-all")
            case "delete":
                result = await api_client.delete(f"/notifications/{notification_id}")
            case "get_preferences":
                result = await api_client.get("/notifications/preferences")
            case "update_preference":
                result = await api_client.put(f"/notifications/preferences/{event_type}", body=data)
            case _:
                return f"Unknown action: {action}. Valid: list, get, count, poll, mark_read, mark_all_read, delete, get_preferences, update_preference"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_documents",
        description=(
            "Manage documents. Actions: list, get, create, update, delete, search, versions."
        ),
    )
    async def aexy_documents(
        action: str,
        workspace_id: str,
        document_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage documents.

        Args:
            action: list, get, create, update, delete, search, versions
            workspace_id: Workspace ID
            document_id: Document ID (required for get, update, delete, versions)
            data: Request body for create/update/search
            params: Query parameters for list
        """
        base = f"/workspaces/{workspace_id}/documents"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{document_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{document_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{document_id}")
            case "search":
                result = await api_client.post(f"{base}/search", body=data)
            case "versions":
                result = await api_client.get(f"{base}/{document_id}/versions")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, search, versions"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_tickets",
        description=(
            "Manage support tickets. Actions: list, get, get_by_number, create, "
            "update, delete, assign, stats, responses, create_task."
        ),
    )
    async def aexy_tickets(
        action: str,
        workspace_id: str,
        ticket_id: str | None = None,
        ticket_number: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage tickets.

        Args:
            action: list, get, get_by_number, create, update, delete, assign, stats, responses, create_task
            workspace_id: Workspace ID
            ticket_id: Ticket ID (for get, update, delete, assign, responses, create_task)
            ticket_number: Ticket number (for get_by_number)
            data: Request body for create/update/assign/responses/create_task
            params: Query parameters for list
        """
        base = f"/workspaces/{workspace_id}/tickets"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{ticket_id}")
            case "get_by_number":
                result = await api_client.get(f"{base}/number/{ticket_number}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{ticket_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{ticket_id}")
            case "assign":
                result = await api_client.post(f"{base}/{ticket_id}/assign", body=data)
            case "stats":
                result = await api_client.get(f"{base}/stats")
            case "responses":
                if data:
                    result = await api_client.post(f"{base}/{ticket_id}/responses", body=data)
                else:
                    result = await api_client.get(f"{base}/{ticket_id}/responses")
            case "create_task":
                result = await api_client.post(f"{base}/{ticket_id}/create-task", body=data)
            case _:
                return f"Unknown action: {action}. Valid: list, get, get_by_number, create, update, delete, assign, stats, responses, create_task"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_tables",
        description=(
            "Manage standalone tables (spreadsheet-like data). "
            "Actions: list, get, create, delete, list_rows, create_row, update_row, delete_row, query."
        ),
    )
    async def aexy_tables(
        action: str,
        workspace_id: str,
        table_id: str | None = None,
        row_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage tables.

        Args:
            action: list, get, create, delete, list_rows, create_row, update_row, delete_row, query
            workspace_id: Workspace ID
            table_id: Table ID (required for most actions)
            row_id: Row ID (for update_row, delete_row)
            data: Request body for create/create_row/update_row/query
            params: Query parameters for list/list_rows
        """
        base = f"/workspaces/{workspace_id}/tables"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{table_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{table_id}")
            case "list_rows":
                result = await api_client.get(f"{base}/{table_id}/rows", params=params)
            case "create_row":
                result = await api_client.post(f"{base}/{table_id}/rows", body=data)
            case "update_row":
                result = await api_client.patch(f"{base}/{table_id}/rows/{row_id}", body=data)
            case "delete_row":
                result = await api_client.delete(f"{base}/{table_id}/rows/{row_id}")
            case "query":
                result = await api_client.post(f"{base}/{table_id}/query", body=data)
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, delete, list_rows, create_row, update_row, delete_row, query"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_integrations",
        description=(
            "Manage integrations (Jira, Linear). "
            "Actions: get_jira, connect_jira, test_jira, sync_jira, disconnect_jira, "
            "get_linear, connect_linear, test_linear, sync_linear, disconnect_linear."
        ),
    )
    async def aexy_integrations(
        action: str,
        workspace_id: str,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage integrations.

        Args:
            action: get_jira, connect_jira, test_jira, sync_jira, disconnect_jira, jira_projects, jira_statuses, get_linear, connect_linear, test_linear, sync_linear, disconnect_linear, linear_teams, linear_states
            workspace_id: Workspace ID
            data: Request body for connect actions
        """
        base = f"/workspaces/{workspace_id}/integrations"

        match action:
            case "get_jira":
                result = await api_client.get(f"{base}/jira")
            case "connect_jira":
                result = await api_client.post(f"{base}/jira", body=data)
            case "test_jira":
                result = await api_client.post(f"{base}/jira/test")
            case "sync_jira":
                result = await api_client.post(f"{base}/jira/sync")
            case "disconnect_jira":
                result = await api_client.delete(f"{base}/jira")
            case "jira_projects":
                result = await api_client.get(f"{base}/jira/projects")
            case "jira_statuses":
                result = await api_client.get(f"{base}/jira/statuses")
            case "get_linear":
                result = await api_client.get(f"{base}/linear")
            case "connect_linear":
                result = await api_client.post(f"{base}/linear", body=data)
            case "test_linear":
                result = await api_client.post(f"{base}/linear/test")
            case "sync_linear":
                result = await api_client.post(f"{base}/linear/sync")
            case "disconnect_linear":
                result = await api_client.delete(f"{base}/linear")
            case "linear_teams":
                result = await api_client.get(f"{base}/linear/teams")
            case "linear_states":
                result = await api_client.get(f"{base}/linear/states")
            case _:
                return f"Unknown action: {action}. Valid: get_jira, connect_jira, test_jira, sync_jira, disconnect_jira, jira_projects, jira_statuses, get_linear, connect_linear, test_linear, sync_linear, disconnect_linear, linear_teams, linear_states"

        return json.dumps(result, indent=2, default=str)
