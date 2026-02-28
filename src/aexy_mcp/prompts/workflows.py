"""Pre-built MCP prompt templates for common Aexy workflows."""

from __future__ import annotations


def register_prompts(app, enable_temporal: bool = True):
    """Register prompt templates."""

    @app.prompt(
        name="sprint_standup",
        description="Daily standup summary — pulls active sprint, lists tasks by status, shows blockers and progress.",
    )
    async def sprint_standup(workspace_id: str, team_id: str) -> str:
        return f"""Please provide a daily standup summary for this team. Follow these steps:

1. Use aexy_sprints with action="get_active", workspace_id="{workspace_id}", team_id="{team_id}" to get the active sprint
2. Use aexy_sprint_tasks with action="list" and the sprint_id from step 1 to get all tasks
3. Use aexy_sprint_analytics with action="metrics" and the sprint_id to get sprint metrics

Then summarize:
- Sprint progress (% complete, days remaining)
- Tasks completed yesterday
- Tasks in progress today
- Blocked tasks with details
- Key metrics (velocity, burndown trend)

Format as a concise standup report."""

    @app.prompt(
        name="sprint_planning",
        description="Sprint planning assistant — shows backlog, velocity trends, capacity, and suggests story points.",
    )
    async def sprint_planning(workspace_id: str, team_id: str) -> str:
        return f"""Help plan the next sprint for this team. Follow these steps:

1. Use aexy_sprints with action="list", workspace_id="{workspace_id}", team_id="{team_id}" to see recent sprints
2. Use aexy_sprint_analytics with action="velocity", team_id="{team_id}" to get velocity trends
3. Use aexy_sprint_analytics with action="carry_over", team_id="{team_id}" to check carry-over patterns
4. Use aexy_sprint_analytics with action="health", team_id="{team_id}" for team health

Then provide:
- Recommended sprint capacity based on velocity trends
- Carry-over items that need attention
- Suggested sprint goal based on team health and capacity
- Recommendations for task distribution"""

    @app.prompt(
        name="crm_pipeline_review",
        description="CRM pipeline review — summarizes records, recent activities, and stale deals.",
    )
    async def crm_pipeline_review(workspace_id: str) -> str:
        return f"""Review the CRM pipeline. Follow these steps:

1. Use aexy_crm_objects with action="list", workspace_id="{workspace_id}" to see CRM object types
2. For each deal/opportunity object type, use aexy_crm_records with action="list" to get records
3. Check for stale records (no recent activity)

Provide:
- Pipeline summary by stage
- Total pipeline value
- Stale deals (no activity in 14+ days)
- Records that need follow-up
- Key metrics and trends"""

    @app.prompt(
        name="weekly_report",
        description="Weekly engineering report — aggregates sprint progress, developer insights, and completed tasks.",
    )
    async def weekly_report(workspace_id: str, team_id: str) -> str:
        return f"""Generate a weekly engineering report. Follow these steps:

1. Use aexy_sprints with action="get_active", workspace_id="{workspace_id}", team_id="{team_id}"
2. Use aexy_sprint_tasks with action="list" to get all tasks for the sprint
3. Use aexy_sprint_analytics with action="metrics" for sprint metrics
4. Use aexy_sprint_analytics with action="velocity", team_id="{team_id}" for velocity data
5. Use aexy_developer_insights with action="team_insights", workspace_id="{workspace_id}", team_id="{team_id}"

Compile a weekly report covering:
- Sprint progress and burndown
- Tasks completed this week
- Key accomplishments
- Blockers and risks
- Velocity trends
- Team health indicators
- Focus areas for next week"""

    if enable_temporal:
        @app.prompt(
            name="debug_workflow",
            description="Debug a Temporal workflow — walks through listing failures, getting history, and identifying root cause.",
        )
        async def debug_workflow(workflow_id: str | None = None) -> str:
            if workflow_id:
                return f"""Debug the Temporal workflow with ID "{workflow_id}". Follow these steps:

1. Use temporal_describe_workflow with workflow_id="{workflow_id}" to get its current status
2. Use temporal_get_workflow_history with workflow_id="{workflow_id}" to see the full event timeline
3. If the workflow is running, use temporal_query_workflow with query_name="get_status" to check current state

Analyze:
- What activity failed and why (look for error messages in failed events)
- How many retries have occurred
- Whether the failure is transient (timeout, connection) or permanent (logic error)
- Suggest remediation steps"""
            else:
                return """Debug recent Temporal workflow failures. Follow these steps:

1. Use temporal_list_workflows with status="Failed" to find recent failures
2. For the most recent failure, use temporal_describe_workflow to get details
3. Use temporal_get_workflow_history to see the full event timeline

Analyze:
- Which activities are failing most often
- Common error patterns
- Whether failures are transient or systematic
- Suggest remediation steps"""

        @app.prompt(
            name="system_health",
            description="System health check — Temporal status, recent failures, schedule health, queue depths.",
        )
        async def system_health() -> str:
            return """Check the overall system health. Follow these steps:

1. Use temporal_system_status to get the aggregate dashboard
2. Use temporal_list_schedules to check schedule health
3. If there are recent failures, use temporal_list_workflows with status="Failed" for details

Report on:
- Workflow counts by status (Running, Completed, Failed)
- Any concerning failure rates
- Paused or failing schedules
- Queue health and any backlogs
- Recommendations for any issues found"""
