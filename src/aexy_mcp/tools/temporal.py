"""Temporal debugging tools — workflow inspection, history parsing, system status."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Any

from temporalio.client import (
    Client,
    WorkflowExecution,
    WorkflowExecutionStatus,
)
from temporalio.common import SearchAttributeKey

from ..temporal_client import get_temporal_client


def _format_timestamp(ts: datetime | None) -> str | None:
    if ts is None:
        return None
    return ts.isoformat()


def _status_name(status: WorkflowExecutionStatus | None) -> str:
    if status is None:
        return "UNKNOWN"
    return status.name


async def _get_client() -> Client:
    return await get_temporal_client()


def register_temporal_tools(app):
    """Register all 8 Temporal debugging tools."""

    @app.tool(
        name="temporal_list_workflows",
        description=(
            "List Temporal workflow executions. Supports filtering by status, type, "
            "and time range using Temporal visibility queries."
        ),
    )
    async def temporal_list_workflows(
        query: str | None = None,
        status: str | None = None,
        workflow_type: str | None = None,
        limit: int = 20,
    ) -> str:
        """List workflow executions.

        Args:
            query: Raw Temporal visibility query (e.g., 'WorkflowType="SingleActivityWorkflow" AND ExecutionStatus="Running"')
            status: Filter by status: Running, Completed, Failed, Canceled, Terminated, TimedOut
            workflow_type: Filter by workflow type name
            limit: Max results (default 20)
        """
        client = await _get_client()

        # Build query from parameters if not provided directly
        if not query:
            conditions = []
            if status:
                conditions.append(f'ExecutionStatus="{status}"')
            if workflow_type:
                conditions.append(f'WorkflowType="{workflow_type}"')
            query = " AND ".join(conditions) if conditions else None

        workflows = []
        count = 0
        async for wf in client.list_workflows(query=query):
            if count >= limit:
                break
            workflows.append({
                "workflow_id": wf.id,
                "run_id": wf.run_id,
                "type": wf.workflow_type,
                "status": _status_name(wf.status),
                "start_time": _format_timestamp(wf.start_time),
                "close_time": _format_timestamp(wf.close_time),
                "task_queue": wf.task_queue,
            })
            count += 1

        return json.dumps({"count": len(workflows), "workflows": workflows}, indent=2, default=str)

    @app.tool(
        name="temporal_describe_workflow",
        description=(
            "Get full description of a workflow execution — status, type, queue, "
            "start/close times, history length, pending activities."
        ),
    )
    async def temporal_describe_workflow(
        workflow_id: str,
        run_id: str | None = None,
    ) -> str:
        """Describe a workflow execution.

        Args:
            workflow_id: Workflow ID
            run_id: Run ID (optional, uses latest run if not specified)
        """
        client = await _get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)
        desc = await handle.describe()

        result = {
            "workflow_id": desc.id,
            "run_id": desc.run_id,
            "type": desc.workflow_type,
            "status": _status_name(desc.status),
            "task_queue": desc.task_queue,
            "start_time": _format_timestamp(desc.start_time),
            "close_time": _format_timestamp(desc.close_time),
            "execution_time": _format_timestamp(desc.execution_time),
            "history_length": desc.history_length,
        }

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="temporal_get_workflow_history",
        description=(
            "Key debugging tool. Parse workflow event history into a readable timeline "
            "showing activity starts/completions, failures with details, retry counts, "
            "signals, timers, and child workflows."
        ),
    )
    async def temporal_get_workflow_history(
        workflow_id: str,
        run_id: str | None = None,
        max_events: int = 100,
    ) -> str:
        """Get and parse workflow event history.

        Args:
            workflow_id: Workflow ID
            run_id: Run ID (optional)
            max_events: Max events to return (default 100)
        """
        client = await _get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)

        events = []
        start_time = None
        count = 0

        async for event in handle.fetch_history_events():
            if count >= max_events:
                break
            count += 1

            event_time = event.event_time.ToDatetime(tzinfo=timezone.utc) if event.event_time else None
            if start_time is None and event_time:
                start_time = event_time

            # Calculate relative time
            relative_ms = 0
            if start_time and event_time:
                relative_ms = int((event_time - start_time).total_seconds() * 1000)

            entry = _parse_event(event, relative_ms)
            if entry:
                events.append(entry)

        # Build readable timeline
        desc = await handle.describe()
        header = f"Workflow History: {workflow_id}"
        if desc.workflow_type:
            header += f" (type={desc.workflow_type})"

        timeline_lines = [header, f"Status: {_status_name(desc.status)}", ""]
        for e in events:
            time_str = _format_relative_time(e["relative_ms"])
            detail = e.get("detail", "")
            timeline_lines.append(f"  [{time_str}] {e['type']} — {detail}")

        timeline = "\n".join(timeline_lines)

        return json.dumps({
            "timeline": timeline,
            "event_count": len(events),
            "events": events,
        }, indent=2, default=str)

    @app.tool(
        name="temporal_query_workflow",
        description=(
            "Query a running workflow's state. For example, query 'get_status' on "
            "CRMAutomationWorkflow to see current node, or custom query handlers."
        ),
    )
    async def temporal_query_workflow(
        workflow_id: str,
        query_name: str,
        run_id: str | None = None,
    ) -> str:
        """Query a running workflow.

        Args:
            workflow_id: Workflow ID
            query_name: Query handler name (e.g., 'get_status')
            run_id: Run ID (optional)
        """
        client = await _get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)

        try:
            result = await handle.query(query_name)
            return json.dumps({"query": query_name, "result": result}, indent=2, default=str)
        except Exception as e:
            return json.dumps({"query": query_name, "error": str(e)}, indent=2)

    @app.tool(
        name="temporal_signal_workflow",
        description=(
            "Send a signal to a running workflow. Examples: 'on_event' to "
            "CRMAutomationWorkflow, 'pause'/'resume' to OutreachSequenceWorkflow."
        ),
    )
    async def temporal_signal_workflow(
        workflow_id: str,
        signal_name: str,
        args: list[Any] | None = None,
        run_id: str | None = None,
    ) -> str:
        """Signal a running workflow.

        Args:
            workflow_id: Workflow ID
            signal_name: Signal handler name (e.g., 'on_event', 'pause', 'resume')
            args: Signal arguments (optional)
            run_id: Run ID (optional)
        """
        client = await _get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)

        await handle.signal(signal_name, args[0] if args and len(args) == 1 else args)

        return json.dumps({
            "status": "signal_sent",
            "workflow_id": workflow_id,
            "signal": signal_name,
        }, indent=2)

    @app.tool(
        name="temporal_cancel_workflow",
        description="Cancel or terminate a workflow execution with a reason.",
    )
    async def temporal_cancel_workflow(
        workflow_id: str,
        reason: str = "",
        terminate: bool = False,
        run_id: str | None = None,
    ) -> str:
        """Cancel or terminate a workflow.

        Args:
            workflow_id: Workflow ID
            reason: Reason for cancellation/termination
            terminate: If True, terminates (force kill) instead of cancelling (graceful)
            run_id: Run ID (optional)
        """
        client = await _get_client()
        handle = client.get_workflow_handle(workflow_id, run_id=run_id)

        if terminate:
            await handle.terminate(reason=reason)
            action = "terminated"
        else:
            await handle.cancel()
            action = "cancelled"

        return json.dumps({
            "status": action,
            "workflow_id": workflow_id,
            "reason": reason,
        }, indent=2)

    @app.tool(
        name="temporal_list_schedules",
        description=(
            "List all registered Temporal schedules with intervals, next run times, "
            "and paused status."
        ),
    )
    async def temporal_list_schedules(
        limit: int = 100,
    ) -> str:
        """List all schedules.

        Args:
            limit: Max results (default 100)
        """
        client = await _get_client()

        schedules = []
        count = 0
        async for schedule in client.list_schedules():
            if count >= limit:
                break
            count += 1

            info = schedule.info
            spec = schedule.schedule.spec if schedule.schedule else None

            entry = {
                "id": schedule.id,
                "paused": info.paused if info else False,
                "note": info.note if info else None,
            }

            if info and info.recent_actions:
                last_action = info.recent_actions[-1]
                entry["last_run"] = _format_timestamp(last_action.start_time) if last_action.start_time else None

            if info and info.next_action_times:
                entry["next_run"] = _format_timestamp(info.next_action_times[0])

            if info and info.num_actions:
                entry["total_runs"] = info.num_actions

            schedules.append(entry)

        return json.dumps({"count": len(schedules), "schedules": schedules}, indent=2, default=str)

    @app.tool(
        name="temporal_system_status",
        description=(
            "Aggregate Temporal dashboard: workflow counts by status/type, "
            "recent failures, schedule health overview."
        ),
    )
    async def temporal_system_status() -> str:
        """Get Temporal system status overview."""
        client = await _get_client()

        # Count workflows by status
        status_counts = {}
        for status_name in ["Running", "Completed", "Failed", "Canceled", "Terminated", "TimedOut"]:
            count = 0
            async for _ in client.list_workflows(query=f'ExecutionStatus="{status_name}"'):
                count += 1
                if count >= 1000:
                    break
            if count > 0:
                status_counts[status_name] = count

        # Recent failures (last 10)
        recent_failures = []
        failure_count = 0
        async for wf in client.list_workflows(query='ExecutionStatus="Failed"'):
            if failure_count >= 10:
                break
            recent_failures.append({
                "workflow_id": wf.id,
                "type": wf.workflow_type,
                "task_queue": wf.task_queue,
                "start_time": _format_timestamp(wf.start_time),
                "close_time": _format_timestamp(wf.close_time),
            })
            failure_count += 1

        # Schedule summary
        schedule_count = 0
        paused_count = 0
        async for schedule in client.list_schedules():
            schedule_count += 1
            if schedule.info and schedule.info.paused:
                paused_count += 1

        result = {
            "workflow_counts_by_status": status_counts,
            "recent_failures": recent_failures,
            "schedules": {
                "total": schedule_count,
                "paused": paused_count,
                "active": schedule_count - paused_count,
            },
        }

        return json.dumps(result, indent=2, default=str)


def _parse_event(event, relative_ms: int) -> dict[str, Any] | None:
    """Parse a history event into a readable entry."""
    event_type = event.event_type
    # event_type is an enum, get the name
    type_name = event_type if isinstance(event_type, str) else event_type.name if hasattr(event_type, 'name') else str(event_type)

    entry = {
        "type": type_name,
        "relative_ms": relative_ms,
        "event_id": event.event_id,
    }

    # Parse specific event types for useful details
    if hasattr(event, 'workflow_execution_started_event_attributes') and event.workflow_execution_started_event_attributes:
        attrs = event.workflow_execution_started_event_attributes
        entry["detail"] = f"type={attrs.workflow_type.name if attrs.workflow_type else '?'}, queue={attrs.task_queue.name if attrs.task_queue else '?'}"

    elif hasattr(event, 'activity_task_scheduled_event_attributes') and event.activity_task_scheduled_event_attributes:
        attrs = event.activity_task_scheduled_event_attributes
        entry["detail"] = f"activity={attrs.activity_type.name if attrs.activity_type else '?'}"

    elif hasattr(event, 'activity_task_completed_event_attributes') and event.activity_task_completed_event_attributes:
        entry["detail"] = "completed"

    elif hasattr(event, 'activity_task_failed_event_attributes') and event.activity_task_failed_event_attributes:
        attrs = event.activity_task_failed_event_attributes
        failure = attrs.failure
        detail = "FAILED"
        if failure:
            detail = f"FAILED: {failure.message}"
            if failure.cause:
                detail += f" (cause: {failure.cause.message})"
        entry["detail"] = detail

    elif hasattr(event, 'activity_task_timed_out_event_attributes') and event.activity_task_timed_out_event_attributes:
        entry["detail"] = "TIMED OUT"

    elif hasattr(event, 'workflow_execution_completed_event_attributes') and event.workflow_execution_completed_event_attributes:
        entry["detail"] = "workflow completed"

    elif hasattr(event, 'workflow_execution_failed_event_attributes') and event.workflow_execution_failed_event_attributes:
        attrs = event.workflow_execution_failed_event_attributes
        failure = attrs.failure
        detail = "workflow FAILED"
        if failure:
            detail = f"workflow FAILED: {failure.message}"
        entry["detail"] = detail

    elif hasattr(event, 'workflow_execution_canceled_event_attributes') and event.workflow_execution_canceled_event_attributes:
        entry["detail"] = "workflow cancelled"

    elif hasattr(event, 'workflow_execution_terminated_event_attributes') and event.workflow_execution_terminated_event_attributes:
        attrs = event.workflow_execution_terminated_event_attributes
        entry["detail"] = f"workflow terminated: {attrs.reason}"

    elif hasattr(event, 'timer_started_event_attributes') and event.timer_started_event_attributes:
        attrs = event.timer_started_event_attributes
        entry["detail"] = f"timer started (id={attrs.timer_id})"

    elif hasattr(event, 'timer_fired_event_attributes') and event.timer_fired_event_attributes:
        attrs = event.timer_fired_event_attributes
        entry["detail"] = f"timer fired (id={attrs.timer_id})"

    elif hasattr(event, 'workflow_execution_signaled_event_attributes') and event.workflow_execution_signaled_event_attributes:
        attrs = event.workflow_execution_signaled_event_attributes
        entry["detail"] = f"signal: {attrs.signal_name}"

    else:
        entry["detail"] = type_name

    return entry


def _format_relative_time(ms: int) -> str:
    """Format milliseconds as MM:SS.mmm."""
    seconds = ms // 1000
    millis = ms % 1000
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}.{millis:03d}"
