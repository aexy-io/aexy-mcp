"""CRM tools — objects, records, automations."""

from __future__ import annotations

import json
from typing import Any


def register_crm_tools(app, api_client):
    """Register CRM-related tools."""

    @app.tool(
        name="aexy_crm_objects",
        description=(
            "Manage CRM object types and their attributes. "
            "Actions: list, get, create, update, delete, list_attributes, create_attribute."
        ),
    )
    async def aexy_crm_objects(
        action: str,
        workspace_id: str,
        object_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage CRM objects (object types/schemas).

        Args:
            action: list, get, create, update, delete, list_attributes, create_attribute
            workspace_id: Workspace ID
            object_id: CRM object type ID (required for get, update, delete, list_attributes, create_attribute)
            data: Request body for create/update/create_attribute
        """
        base = f"/workspaces/{workspace_id}/crm/objects"

        match action:
            case "list":
                result = await api_client.get(base)
            case "get":
                result = await api_client.get(f"{base}/{object_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{object_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{object_id}")
            case "list_attributes":
                result = await api_client.get(f"{base}/{object_id}/attributes")
            case "create_attribute":
                result = await api_client.post(f"{base}/{object_id}/attributes", body=data)
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, list_attributes, create_attribute"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_crm_records",
        description=(
            "Manage CRM records (contacts, companies, deals, etc.). "
            "Actions: list, get, create, update, delete, bulk_create, search, notes, activities."
        ),
    )
    async def aexy_crm_records(
        action: str,
        workspace_id: str,
        object_id: str,
        record_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage CRM records.

        Args:
            action: list, get, create, update, delete, bulk_create, search, notes, activities
            workspace_id: Workspace ID
            object_id: CRM object type ID (e.g., 'contacts', 'companies')
            record_id: Record ID (required for get, update, delete, notes, activities)
            data: Request body for create/update/bulk_create/search
            params: Query parameters for list/filter
        """
        base = f"/workspaces/{workspace_id}/crm/objects/{object_id}/records"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{record_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{record_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{record_id}")
            case "bulk_create":
                result = await api_client.post(f"{base}/bulk", body=data)
            case "search":
                result = await api_client.post(
                    f"/workspaces/{workspace_id}/crm/objects/{object_id}/search",
                    body=data,
                )
            case "notes":
                if data:
                    result = await api_client.post(f"{base}/{record_id}/notes", body=data)
                else:
                    result = await api_client.get(f"{base}/{record_id}/notes")
            case "activities":
                result = await api_client.get(f"{base}/{record_id}/activities")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, bulk_create, search, notes, activities"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_crm_automations",
        description=(
            "Manage CRM automations and sequences. "
            "Actions: list, get, create, update, delete, toggle, trigger, runs, "
            "list_sequences, get_sequence, create_sequence, toggle_sequence, "
            "enroll_sequence, sequence_enrollments."
        ),
    )
    async def aexy_crm_automations(
        action: str,
        workspace_id: str,
        automation_id: str | None = None,
        sequence_id: str | None = None,
        run_id: str | None = None,
        enrollment_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage CRM automations.

        Args:
            action: list, get, create, update, delete, toggle, trigger, runs, get_run, list_sequences, get_sequence, create_sequence, toggle_sequence, enroll_sequence, sequence_enrollments
            workspace_id: Workspace ID
            automation_id: Automation ID
            sequence_id: Sequence ID (for sequence actions)
            run_id: Run ID (for get_run)
            enrollment_id: Enrollment ID (for pause/resume/unenroll)
            data: Request body
        """
        base = f"/workspaces/{workspace_id}/crm"

        match action:
            case "list":
                result = await api_client.get(f"{base}/automations")
            case "get":
                result = await api_client.get(f"{base}/automations/{automation_id}")
            case "create":
                result = await api_client.post(f"{base}/automations", body=data)
            case "update":
                result = await api_client.patch(f"{base}/automations/{automation_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/automations/{automation_id}")
            case "toggle":
                result = await api_client.post(f"{base}/automations/{automation_id}/toggle")
            case "trigger":
                result = await api_client.post(f"{base}/automations/{automation_id}/trigger")
            case "runs":
                result = await api_client.get(f"{base}/automations/{automation_id}/runs")
            case "get_run":
                result = await api_client.get(f"{base}/automation-runs/{run_id}")
            case "list_sequences":
                result = await api_client.get(f"{base}/sequences")
            case "get_sequence":
                result = await api_client.get(f"{base}/sequences/{sequence_id}")
            case "create_sequence":
                result = await api_client.post(f"{base}/sequences", body=data)
            case "toggle_sequence":
                result = await api_client.post(f"{base}/sequences/{sequence_id}/toggle")
            case "enroll_sequence":
                result = await api_client.post(f"{base}/sequences/{sequence_id}/enroll", body=data)
            case "sequence_enrollments":
                result = await api_client.get(f"{base}/sequences/{sequence_id}/enrollments")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, toggle, trigger, runs, get_run, list_sequences, get_sequence, create_sequence, toggle_sequence, enroll_sequence, sequence_enrollments"

        return json.dumps(result, indent=2, default=str)
