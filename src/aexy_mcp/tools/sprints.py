"""Sprint management tools — sprints, sprint tasks, sprint analytics."""

from __future__ import annotations

import json
from typing import Any


def register_sprint_tools(app, api_client):
    """Register sprint-related tools."""

    @app.tool(
        name="aexy_sprints",
        description=(
            "Manage sprints in Aexy. Actions: list, get, get_active, create, update, "
            "delete, start, complete, review, retro, stats, carry_over."
        ),
    )
    async def aexy_sprints(
        action: str,
        workspace_id: str,
        team_id: str,
        sprint_id: str | None = None,
        target_sprint_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage sprints.

        Args:
            action: list, get, get_active, create, update, delete, start, complete, review, retro, stats, carry_over
            workspace_id: Workspace ID
            team_id: Team ID
            sprint_id: Sprint ID (required for get, update, delete, start, complete, review, retro, stats, carry_over)
            target_sprint_id: Target sprint for carry_over action
            data: Request body for create/update actions
        """
        base = f"/workspaces/{workspace_id}/teams/{team_id}/sprints"

        match action:
            case "list":
                result = await api_client.get(base)
            case "get":
                result = await api_client.get(f"{base}/{sprint_id}")
            case "get_active":
                result = await api_client.get(f"{base}/active")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{sprint_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{sprint_id}")
            case "start":
                result = await api_client.post(f"{base}/{sprint_id}/start")
            case "complete":
                result = await api_client.post(f"{base}/{sprint_id}/complete")
            case "review":
                result = await api_client.post(f"{base}/{sprint_id}/review")
            case "retro":
                result = await api_client.post(f"{base}/{sprint_id}/retro")
            case "stats":
                result = await api_client.get(f"{base}/{sprint_id}/stats")
            case "carry_over":
                result = await api_client.post(f"{base}/{sprint_id}/carry-over/{target_sprint_id}")
            case _:
                return f"Unknown action: {action}. Valid: list, get, get_active, create, update, delete, start, complete, review, retro, stats, carry_over"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_sprint_tasks",
        description=(
            "Manage sprint tasks. Actions: list, get, create, update, delete, assign, "
            "unassign, update_status, bulk_status, bulk_assign, suggest_assignments, "
            "subtasks, activities, comments, capacity, completion_prediction."
        ),
    )
    async def aexy_sprint_tasks(
        action: str,
        sprint_id: str,
        task_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage sprint tasks.

        Args:
            action: list, get, create, update, delete, assign, unassign, update_status, bulk_status, bulk_assign, suggest_assignments, subtasks, activities, comments, capacity, completion_prediction
            sprint_id: Sprint ID
            task_id: Task ID (required for get, update, delete, assign, unassign, update_status, subtasks, activities, comments)
            data: Request body for create/update/assign/bulk actions
            params: Query parameters for list/filter
        """
        base = f"/sprints/{sprint_id}/tasks"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{task_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{task_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{task_id}")
            case "assign":
                result = await api_client.post(f"{base}/{task_id}/assign", body=data)
            case "unassign":
                result = await api_client.delete(f"{base}/{task_id}/assign")
            case "update_status":
                result = await api_client.patch(f"{base}/{task_id}/status", body=data)
            case "bulk_status":
                result = await api_client.post(f"{base}/bulk-status", body=data)
            case "bulk_assign":
                result = await api_client.post(f"{base}/bulk-assign", body=data)
            case "suggest_assignments":
                result = await api_client.post(f"{base}/suggest-assignments")
            case "subtasks":
                result = await api_client.get(f"{base}/{task_id}/subtasks")
            case "activities":
                result = await api_client.get(f"{base}/{task_id}/activities")
            case "comments":
                if data:
                    result = await api_client.post(f"{base}/{task_id}/comments", body=data)
                else:
                    return "Provide data with comment content to post a comment"
            case "capacity":
                result = await api_client.get(f"{base}/capacity")
            case "completion_prediction":
                result = await api_client.get(f"{base}/completion-prediction")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, assign, unassign, update_status, bulk_status, bulk_assign, suggest_assignments, subtasks, activities, comments, capacity, completion_prediction"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_sprint_analytics",
        description=(
            "Sprint and team analytics. Actions: burndown, cycle_time, metrics, "
            "velocity, velocity_predict, carry_over, carry_over_chronic, health."
        ),
    )
    async def aexy_sprint_analytics(
        action: str,
        sprint_id: str | None = None,
        team_id: str | None = None,
    ) -> str:
        """Get sprint and team analytics.

        Args:
            action: burndown, cycle_time, metrics, velocity, velocity_predict, carry_over, carry_over_chronic, health
            sprint_id: Sprint ID (for burndown, cycle_time, metrics)
            team_id: Team ID (for velocity, velocity_predict, carry_over, carry_over_chronic, health)
        """
        match action:
            case "burndown":
                result = await api_client.get(f"/sprints/{sprint_id}/burndown")
            case "cycle_time":
                result = await api_client.get(f"/sprints/{sprint_id}/analytics/cycle-time")
            case "metrics":
                result = await api_client.get(f"/sprints/{sprint_id}/metrics")
            case "velocity":
                result = await api_client.get(f"/teams/{team_id}/velocity")
            case "velocity_predict":
                result = await api_client.get(f"/teams/{team_id}/velocity/predict")
            case "carry_over":
                result = await api_client.get(f"/teams/{team_id}/carry-over")
            case "carry_over_chronic":
                result = await api_client.get(f"/teams/{team_id}/carry-over/chronic")
            case "health":
                result = await api_client.get(f"/teams/{team_id}/health")
            case _:
                return f"Unknown action: {action}. Valid: burndown, cycle_time, metrics, velocity, velocity_predict, carry_over, carry_over_chronic, health"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_projects",
        description="Manage projects. Actions: list, get, create, update, delete, members, teams.",
    )
    async def aexy_projects(
        action: str,
        workspace_id: str,
        project_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage projects.

        Args:
            action: list, get, create, update, delete, members, teams
            workspace_id: Workspace ID
            project_id: Project ID (required for get, update, delete, members, teams)
            data: Request body for create/update
        """
        base = f"/workspaces/{workspace_id}/projects"

        match action:
            case "list":
                result = await api_client.get(base)
            case "get":
                result = await api_client.get(f"{base}/{project_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{project_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{project_id}")
            case "members":
                result = await api_client.get(f"{base}/{project_id}/members")
            case "teams":
                result = await api_client.get(f"{base}/{project_id}/teams")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, members, teams"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_epics",
        description="Manage epics. Actions: list, get, create, update, delete, add_tasks, timeline, progress, burndown.",
    )
    async def aexy_epics(
        action: str,
        workspace_id: str,
        epic_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage epics.

        Args:
            action: list, get, create, update, delete, add_tasks, timeline, progress, burndown
            workspace_id: Workspace ID
            epic_id: Epic ID (required for get, update, delete, add_tasks, timeline, progress, burndown)
            data: Request body for create/update/add_tasks
        """
        base = f"/workspaces/{workspace_id}/epics"

        match action:
            case "list":
                result = await api_client.get(base)
            case "get":
                result = await api_client.get(f"{base}/{epic_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{epic_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/{epic_id}")
            case "add_tasks":
                result = await api_client.post(f"{base}/{epic_id}/add-tasks", body=data)
            case "timeline":
                result = await api_client.get(f"{base}/{epic_id}/timeline")
            case "progress":
                result = await api_client.get(f"{base}/{epic_id}/progress")
            case "burndown":
                result = await api_client.get(f"{base}/{epic_id}/burndown")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, add_tasks, timeline, progress, burndown"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_bugs",
        description=(
            "Track and manage bugs. Actions: list, get, create, update, stats, "
            "confirm, fix, verify, close, reopen, link_story, link_task, activity, comments."
        ),
    )
    async def aexy_bugs(
        action: str,
        workspace_id: str,
        bug_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage bugs.

        Args:
            action: list, get, create, update, stats, confirm, fix, verify, close, reopen, link_story, link_task, activity, comments
            workspace_id: Workspace ID
            bug_id: Bug ID (required for most actions except list, stats, create)
            data: Request body for create/update/link/comments
        """
        base = f"/workspaces/{workspace_id}/bugs"

        match action:
            case "list":
                result = await api_client.get(base)
            case "get":
                result = await api_client.get(f"{base}/{bug_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{bug_id}", body=data)
            case "stats":
                result = await api_client.get(f"{base}/stats")
            case "confirm":
                result = await api_client.post(f"{base}/{bug_id}/confirm")
            case "fix":
                result = await api_client.post(f"{base}/{bug_id}/fix")
            case "verify":
                result = await api_client.post(f"{base}/{bug_id}/verify")
            case "close":
                result = await api_client.post(f"{base}/{bug_id}/close")
            case "reopen":
                result = await api_client.post(f"{base}/{bug_id}/reopen")
            case "link_story":
                result = await api_client.post(f"{base}/{bug_id}/link-story", body=data)
            case "link_task":
                result = await api_client.post(f"{base}/{bug_id}/link-task", body=data)
            case "activity":
                result = await api_client.get(f"{base}/{bug_id}/activity")
            case "comments":
                result = await api_client.post(f"{base}/{bug_id}/comments", body=data)
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, stats, confirm, fix, verify, close, reopen, link_story, link_task, activity, comments"

        return json.dumps(result, indent=2, default=str)
