"""Analytics tools — team analytics, developer insights, compliance, assessments."""

from __future__ import annotations

import json
from typing import Any


def register_analytics_tools(app, api_client):
    """Register analytics and extended tools."""

    @app.tool(
        name="aexy_analytics",
        description=(
            "Team and developer analytics. "
            "Actions: skills_heatmap, activity_heatmap, productivity, workload, collaboration."
        ),
    )
    async def aexy_analytics(
        action: str,
        developer_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Get analytics data.

        Args:
            action: skills_heatmap, activity_heatmap, productivity, workload, collaboration
            developer_id: Developer ID (for activity_heatmap)
            data: Request body with filters for heatmap/productivity/workload/collaboration
        """
        match action:
            case "skills_heatmap":
                result = await api_client.post("/analytics/heatmap/skills", body=data)
            case "activity_heatmap":
                result = await api_client.get(f"/analytics/heatmap/activity/{developer_id}")
            case "productivity":
                result = await api_client.post("/analytics/productivity", body=data)
            case "workload":
                result = await api_client.post("/analytics/workload", body=data)
            case "collaboration":
                result = await api_client.post("/analytics/collaboration", body=data)
            case _:
                return f"Unknown action: {action}. Valid: skills_heatmap, activity_heatmap, productivity, workload, collaboration"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_developer_insights",
        description=(
            "Developer insights and snapshots. "
            "Actions: get_snapshot, get_trends, team_insights, leaderboard."
        ),
    )
    async def aexy_developer_insights(
        action: str,
        workspace_id: str,
        developer_id: str | None = None,
        team_id: str | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Get developer insights.

        Args:
            action: get_snapshot, get_trends, team_insights, leaderboard
            workspace_id: Workspace ID
            developer_id: Developer ID (for get_snapshot, get_trends)
            team_id: Team ID (for team_insights, leaderboard)
            params: Query parameters (time period, etc.)
        """
        base = f"/workspaces/{workspace_id}/developer-insights"

        match action:
            case "get_snapshot":
                result = await api_client.get(f"{base}/developers/{developer_id}/snapshot", params=params)
            case "get_trends":
                result = await api_client.get(f"{base}/developers/{developer_id}/trends", params=params)
            case "team_insights":
                result = await api_client.get(f"{base}/teams/{team_id}", params=params)
            case "leaderboard":
                result = await api_client.get(f"{base}/teams/{team_id}/leaderboard", params=params)
            case _:
                return f"Unknown action: {action}. Valid: get_snapshot, get_trends, team_insights, leaderboard"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_compliance",
        description=(
            "Compliance management — training, certifications, audit logs. "
            "Actions: list_training, get_training, create_training, list_certifications, "
            "overview, developer_compliance, expiring, overdue, audit_logs."
        ),
    )
    async def aexy_compliance(
        action: str,
        training_id: str | None = None,
        developer_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage compliance.

        Args:
            action: list_training, get_training, create_training, list_certifications, create_certification, overview, developer_compliance, expiring, overdue, audit_logs
            training_id: Training ID (for get_training)
            developer_id: Developer ID (for developer_compliance)
            data: Request body for create actions
        """
        match action:
            case "list_training":
                result = await api_client.get("/compliance/mandatory-training")
            case "get_training":
                result = await api_client.get(f"/compliance/mandatory-training/{training_id}")
            case "create_training":
                result = await api_client.post("/compliance/mandatory-training", body=data)
            case "list_certifications":
                result = await api_client.get("/compliance/certifications")
            case "create_certification":
                result = await api_client.post("/compliance/certifications", body=data)
            case "overview":
                result = await api_client.get("/compliance/overview")
            case "developer_compliance":
                result = await api_client.get(f"/compliance/developer-compliance/{developer_id}")
            case "expiring":
                result = await api_client.get("/compliance/expiring-certifications")
            case "overdue":
                result = await api_client.get("/compliance/overdue-assignments")
            case "audit_logs":
                result = await api_client.get("/compliance/audit-logs")
            case _:
                return f"Unknown action: {action}. Valid: list_training, get_training, create_training, list_certifications, create_certification, overview, developer_compliance, expiring, overdue, audit_logs"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_assessments",
        description=(
            "Manage assessments. Actions: list, get, create, update, delete, publish, metrics."
        ),
    )
    async def aexy_assessments(
        action: str,
        assessment_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage assessments.

        Args:
            action: list, get, create, update, delete, publish, metrics
            assessment_id: Assessment ID (required for get, update, delete, publish, metrics)
            data: Request body for create/update
            params: Query parameters for list
        """
        match action:
            case "list":
                result = await api_client.get("/assessments", params=params)
            case "get":
                result = await api_client.get(f"/assessments/{assessment_id}")
            case "create":
                result = await api_client.post("/assessments", body=data)
            case "update":
                result = await api_client.patch(f"/assessments/{assessment_id}", body=data)
            case "delete":
                result = await api_client.delete(f"/assessments/{assessment_id}")
            case "publish":
                result = await api_client.post(f"/assessments/{assessment_id}/publish")
            case "metrics":
                result = await api_client.get(f"/assessments/{assessment_id}/metrics")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, publish, metrics"

        return json.dumps(result, indent=2, default=str)
