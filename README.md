# Aexy MCP Server

MCP (Model Context Protocol) server for the Aexy Engineering OS platform. Provides natural language access to sprints, CRM, AI agents, email marketing, analytics, and Temporal workflow debugging.

## Setup

### Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- Running Aexy backend (at `http://localhost:8000`)
- JWT token for API auth

### Install

```bash
cd mcp-server
uv sync
```

### Generate API Token

```bash
# From the project root
docker exec aexy-backend python scripts/generate_test_token.py --first
```

Or export directly:

```bash
export AEXY_API_TOKEN=$(cd backend && python scripts/generate_test_token.py --first 2>/dev/null | grep -A1 "Token:" | tail -1)
```

## Configuration

### Claude Code

Add to your project's `.claude/settings.local.json`:

```json
{
  "mcpServers": {
    "aexy": {
      "command": "uv",
      "args": ["run", "--directory", "mcp-server", "aexy-mcp"],
      "env": {
        "AEXY_API_URL": "http://localhost:8000/api/v1",
        "AEXY_API_TOKEN": "<your-jwt-token>",
        "TEMPORAL_ADDRESS": "localhost:7233"
      }
    }
  }
}
```

### Claude Cowork (for non-developer users)

Disable Temporal debugging tools for non-technical users:

```json
{
  "mcpServers": {
    "aexy": {
      "command": "uv",
      "args": ["run", "--directory", "mcp-server", "aexy-mcp"],
      "env": {
        "AEXY_API_URL": "http://localhost:8000/api/v1",
        "AEXY_API_TOKEN": "<your-jwt-token>",
        "AEXY_ENABLE_TEMPORAL": "false"
      }
    }
  }
}
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `AEXY_API_URL` | `http://localhost:8000/api/v1` | Aexy backend API URL |
| `AEXY_API_TOKEN` | (none) | JWT token for authentication |
| `TEMPORAL_ADDRESS` | `localhost:7233` | Temporal server address |
| `TEMPORAL_NAMESPACE` | `default` | Temporal namespace |
| `AEXY_ENABLE_TEMPORAL` | `true` | Enable/disable Temporal tools |

## Tools

### Generic Gateway (1 tool)

| Tool | Description |
|------|-------------|
| `aexy_api` | Call any Aexy API endpoint directly (method, path, body, query_params) |

### Sprint & Project Management (6 tools)

| Tool | Actions |
|------|---------|
| `aexy_sprints` | list, get, get_active, create, update, delete, start, complete, review, retro, stats, carry_over |
| `aexy_sprint_tasks` | list, get, create, update, delete, assign, unassign, update_status, bulk_status, bulk_assign, suggest_assignments, subtasks, activities, comments, capacity, completion_prediction |
| `aexy_sprint_analytics` | burndown, cycle_time, metrics, velocity, velocity_predict, carry_over, carry_over_chronic, health |
| `aexy_projects` | list, get, create, update, delete, members, teams |
| `aexy_epics` | list, get, create, update, delete, add_tasks, timeline, progress, burndown |
| `aexy_bugs` | list, get, create, update, stats, confirm, fix, verify, close, reopen, link_story, link_task, activity, comments |

### CRM (3 tools)

| Tool | Actions |
|------|---------|
| `aexy_crm_objects` | list, get, create, update, delete, list_attributes, create_attribute |
| `aexy_crm_records` | list, get, create, update, delete, bulk_create, search, notes, activities |
| `aexy_crm_automations` | list, get, create, update, delete, toggle, trigger, runs, get_run, list_sequences, get_sequence, create_sequence, toggle_sequence, enroll_sequence, sequence_enrollments |

### AI Agents & Workflows (3 tools)

| Tool | Actions |
|------|---------|
| `aexy_agents` | list, get, create, update, delete, execute, list_conversations, get_conversation, get_metrics, list_executions |
| `aexy_agent_policies` | list, get, create, update, delete, policy_decisions, config_audit |
| `aexy_workflows` | get, update, validate, publish, list_executions, get_execution |

### Platform (6 tools)

| Tool | Actions |
|------|---------|
| `aexy_workspaces` | list, get, get_my, create, update, members, get_member, teams, permissions |
| `aexy_notifications` | list, get, count, poll, mark_read, mark_all_read, delete, get_preferences, update_preference |
| `aexy_documents` | list, get, create, update, delete, search, versions |
| `aexy_tickets` | list, get, get_by_number, create, update, delete, assign, stats, responses, create_task |
| `aexy_tables` | list, get, create, delete, list_rows, create_row, update_row, delete_row, query |
| `aexy_integrations` | get_jira, connect_jira, test_jira, sync_jira, disconnect_jira, get_linear, connect_linear, test_linear, sync_linear, disconnect_linear |

### Email & GTM (4 tools)

| Tool | Actions |
|------|---------|
| `aexy_email_campaigns` | list, get, create, update, delete, duplicate, schedule, send, pause, resume, cancel, test, audience_count, recipients, analytics, analytics_timeline, analytics_links, analytics_overview, analytics_trends |
| `aexy_email_infrastructure` | list_domains, get_domain, create_domain, verify_domain, domain_health, warming_status, warming_start, warming_pause, list_providers, get_provider, create_provider, test_provider |
| `aexy_gtm_leads` | list, get, create, update, score, activities |
| `aexy_gtm_sequences` | list, get, create, enroll, pause, stats |

### Analytics (4 tools)

| Tool | Actions |
|------|---------|
| `aexy_analytics` | skills_heatmap, activity_heatmap, productivity, workload, collaboration |
| `aexy_developer_insights` | get_snapshot, get_trends, team_insights, leaderboard |
| `aexy_compliance` | list_training, get_training, create_training, list_certifications, overview, developer_compliance, expiring, overdue, audit_logs |
| `aexy_assessments` | list, get, create, update, delete, publish, metrics |

### Temporal Debugging (8 tools)

| Tool | Description |
|------|-------------|
| `temporal_list_workflows` | List workflows with visibility queries, filter by status/type |
| `temporal_describe_workflow` | Full workflow description — status, type, queue, times |
| `temporal_get_workflow_history` | Parse event history into readable timeline with failure details |
| `temporal_query_workflow` | Query running workflow state |
| `temporal_signal_workflow` | Send signals to running workflows |
| `temporal_cancel_workflow` | Cancel or terminate workflows |
| `temporal_list_schedules` | List all registered schedules |
| `temporal_system_status` | Aggregate dashboard with workflow counts, failures, schedule health |

## Resources

| URI | Description |
|-----|-------------|
| `aexy://openapi-spec` | Full OpenAPI specification |
| `aexy://task-queues` | Temporal task queue definitions |
| `aexy://temporal/schedules` | Live schedule data from Temporal |

## Prompts

| Prompt | Description |
|--------|-------------|
| `sprint_standup` | Daily standup summary |
| `sprint_planning` | Sprint planning assistant |
| `crm_pipeline_review` | CRM pipeline review |
| `weekly_report` | Weekly engineering report |
| `debug_workflow` | Temporal workflow debugging walkthrough |
| `system_health` | System health check |

## Development

```bash
cd mcp-server

# Run directly
uv run aexy-mcp

# Install in dev mode
uv pip install -e .

# Run with environment variables
AEXY_API_URL=http://localhost:8000/api/v1 \
AEXY_API_TOKEN=your-token \
uv run aexy-mcp
```
