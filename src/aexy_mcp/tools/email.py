"""Email and GTM tools — campaigns, infrastructure, leads, sequences."""

from __future__ import annotations

import json
from typing import Any


def register_email_tools(app, api_client):
    """Register email and GTM tools."""

    @app.tool(
        name="aexy_email_campaigns",
        description=(
            "Manage email marketing campaigns. "
            "Actions: list, get, create, update, delete, duplicate, schedule, send, "
            "pause, resume, cancel, test, audience_count, recipients, analytics, "
            "analytics_timeline, analytics_links, analytics_overview, analytics_trends."
        ),
    )
    async def aexy_email_campaigns(
        action: str,
        workspace_id: str,
        campaign_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage email campaigns.

        Args:
            action: list, get, create, update, delete, duplicate, schedule, send, pause, resume, cancel, test, audience_count, recipients, analytics, analytics_timeline, analytics_links, analytics_overview, analytics_trends
            workspace_id: Workspace ID
            campaign_id: Campaign ID (required for most actions)
            data: Request body for create/update/schedule/send/test
            params: Query parameters
        """
        base = f"/workspaces/{workspace_id}/email-marketing"

        match action:
            case "list":
                result = await api_client.get(f"{base}/campaigns", params=params)
            case "get":
                result = await api_client.get(f"{base}/campaigns/{campaign_id}")
            case "create":
                result = await api_client.post(f"{base}/campaigns", body=data)
            case "update":
                result = await api_client.patch(f"{base}/campaigns/{campaign_id}", body=data)
            case "delete":
                result = await api_client.delete(f"{base}/campaigns/{campaign_id}")
            case "duplicate":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/duplicate")
            case "schedule":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/schedule", body=data)
            case "send":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/send")
            case "pause":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/pause")
            case "resume":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/resume")
            case "cancel":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/cancel")
            case "test":
                result = await api_client.post(f"{base}/campaigns/{campaign_id}/test", body=data)
            case "audience_count":
                result = await api_client.get(f"{base}/campaigns/{campaign_id}/audience-count")
            case "recipients":
                result = await api_client.get(f"{base}/campaigns/{campaign_id}/recipients", params=params)
            case "analytics":
                result = await api_client.get(f"{base}/campaigns/{campaign_id}/analytics")
            case "analytics_timeline":
                result = await api_client.get(f"{base}/campaigns/{campaign_id}/analytics/timeline")
            case "analytics_links":
                result = await api_client.get(f"{base}/campaigns/{campaign_id}/analytics/links")
            case "analytics_overview":
                result = await api_client.get(f"{base}/analytics/overview")
            case "analytics_trends":
                result = await api_client.get(f"{base}/analytics/trends")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, delete, duplicate, schedule, send, pause, resume, cancel, test, audience_count, recipients, analytics, analytics_timeline, analytics_links, analytics_overview, analytics_trends"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_email_infrastructure",
        description=(
            "Manage email infrastructure — domains, providers, warming, health. "
            "Actions: list_domains, get_domain, verify_domain, domain_health, "
            "warming_status, warming_start, warming_pause, list_providers, "
            "get_provider, test_provider."
        ),
    )
    async def aexy_email_infrastructure(
        action: str,
        workspace_id: str,
        domain_id: str | None = None,
        provider_id: str | None = None,
        data: dict[str, Any] | None = None,
    ) -> str:
        """Manage email infrastructure.

        Args:
            action: list_domains, get_domain, create_domain, verify_domain, domain_health, domain_health_history, warming_status, warming_progress, warming_start, warming_pause, warming_resume, isp_metrics, list_providers, get_provider, create_provider, test_provider
            workspace_id: Workspace ID
            domain_id: Domain ID (for domain actions)
            provider_id: Provider ID (for provider actions)
            data: Request body for create actions
        """
        base = f"/workspaces/{workspace_id}/email-infrastructure"

        match action:
            case "list_domains":
                result = await api_client.get(f"{base}/domains")
            case "get_domain":
                result = await api_client.get(f"{base}/domains/{domain_id}")
            case "create_domain":
                result = await api_client.post(f"{base}/domains", body=data)
            case "verify_domain":
                result = await api_client.post(f"{base}/domains/{domain_id}/verify")
            case "domain_health":
                result = await api_client.get(f"{base}/domains/{domain_id}/health")
            case "domain_health_history":
                result = await api_client.get(f"{base}/domains/{domain_id}/health/history")
            case "warming_status":
                result = await api_client.get(f"{base}/domains/{domain_id}/warming/status")
            case "warming_progress":
                result = await api_client.get(f"{base}/domains/{domain_id}/warming/progress")
            case "warming_start":
                result = await api_client.post(f"{base}/domains/{domain_id}/warming/start")
            case "warming_pause":
                result = await api_client.post(f"{base}/domains/{domain_id}/warming/pause")
            case "warming_resume":
                result = await api_client.post(f"{base}/domains/{domain_id}/warming/resume")
            case "isp_metrics":
                result = await api_client.get(f"{base}/domains/{domain_id}/isp-metrics")
            case "list_providers":
                result = await api_client.get(f"{base}/providers")
            case "get_provider":
                result = await api_client.get(f"{base}/providers/{provider_id}")
            case "create_provider":
                result = await api_client.post(f"{base}/providers", body=data)
            case "test_provider":
                result = await api_client.post(f"{base}/providers/{provider_id}/test")
            case _:
                return f"Unknown action: {action}. Valid: list_domains, get_domain, create_domain, verify_domain, domain_health, domain_health_history, warming_status, warming_progress, warming_start, warming_pause, warming_resume, isp_metrics, list_providers, get_provider, create_provider, test_provider"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_gtm_leads",
        description=(
            "Manage GTM leads. Use the generic aexy_api tool for full GTM access. "
            "Actions: list, get, create, update, score, activities."
        ),
    )
    async def aexy_gtm_leads(
        action: str,
        workspace_id: str,
        lead_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage GTM leads.

        Args:
            action: list, get, create, update, score, activities
            workspace_id: Workspace ID
            lead_id: Lead ID (for get, update, score, activities)
            data: Request body for create/update
            params: Query parameters for list
        """
        base = f"/workspaces/{workspace_id}/gtm/leads"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{lead_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "update":
                result = await api_client.patch(f"{base}/{lead_id}", body=data)
            case "score":
                result = await api_client.post(f"{base}/{lead_id}/score")
            case "activities":
                result = await api_client.get(f"{base}/{lead_id}/activities")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, update, score, activities"

        return json.dumps(result, indent=2, default=str)

    @app.tool(
        name="aexy_gtm_sequences",
        description=(
            "Manage GTM outreach sequences. "
            "Actions: list, get, create, enroll, pause, stats."
        ),
    )
    async def aexy_gtm_sequences(
        action: str,
        workspace_id: str,
        sequence_id: str | None = None,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> str:
        """Manage GTM sequences.

        Args:
            action: list, get, create, enroll, pause, stats
            workspace_id: Workspace ID
            sequence_id: Sequence ID (for get, enroll, pause, stats)
            data: Request body for create/enroll
            params: Query parameters
        """
        base = f"/workspaces/{workspace_id}/gtm/sequences"

        match action:
            case "list":
                result = await api_client.get(base, params=params)
            case "get":
                result = await api_client.get(f"{base}/{sequence_id}")
            case "create":
                result = await api_client.post(base, body=data)
            case "enroll":
                result = await api_client.post(f"{base}/{sequence_id}/enroll", body=data)
            case "pause":
                result = await api_client.post(f"{base}/{sequence_id}/pause")
            case "stats":
                result = await api_client.get(f"{base}/{sequence_id}/stats")
            case _:
                return f"Unknown action: {action}. Valid: list, get, create, enroll, pause, stats"

        return json.dumps(result, indent=2, default=str)
