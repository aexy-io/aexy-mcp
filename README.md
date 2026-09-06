# aexy-mcp

A stdio bridge to the Aexy MCP server. It holds no tools of its own: every
JSON-RPC message from your client is forwarded to `POST {AEXY_API_URL}/mcp`
with your API token, and the answer is written back. The tool list, the
permission checks, workspace policies and the audit ledger all live on the
server, so they are identical whichever way you connect.

**You may not need this.** Clients that speak streamable HTTP — ChatGPT, Claude
Code, Claude Desktop — can connect to the URL directly and sign in through the
browser:

```bash
claude mcp add --transport http aexy https://api.aexy.io/api/v1/mcp
```

Use the bridge for clients that can only launch a local process.

## Setup

1. Create an API token in Aexy under **Settings → API Tokens**. The token
   authenticates as you and carries only your permissions. For an unattended
   agent, an admin can instead create an **agent principal** under
   **Settings → Agent Principals** and issue it a token — it then acts as
   itself, scoped to the capabilities chosen for it.
2. Add the server to your client. Every recipe is the same three facts:

```json
{
  "mcpServers": {
    "aexy": {
      "command": "uvx",
      "args": ["aexy-mcp@latest"],
      "env": {
        "AEXY_API_URL": "https://api.aexy.io/api/v1",
        "AEXY_API_TOKEN": "<your-api-token>",
        "AEXY_WORKSPACE_ID": "<only if you belong to more than one workspace>"
      }
    }
  }
}
```

3. Restart the client.

## Environment variables

| Variable | Meaning |
| --- | --- |
| `AEXY_API_URL` | Backend API base URL, e.g. `https://api.aexy.io/api/v1` |
| `AEXY_API_TOKEN` | Your token from Settings → API Tokens, or a principal's token |
| `AEXY_WORKSPACE_ID` | Which workspace to act in. Required only when the token's owner is in several; a principal is already bound to one |
| `AEXY_TIMEOUT_SECONDS` | Per-request timeout (default 90) |

## What changed in 1.0

Versions before 1.0 were a full MCP server with 27 hand-written tools and direct
Temporal access. Four of those tools called API paths that did not exist, and
because they authenticated against the REST API with a personal token, the
backend could not tell an agent's write from a person's — governance, the
review gate and the audit ledger were all skipped. 1.0 removes all of it. The
server is the backend; this is a cable.

## Development

```bash
uv sync
AEXY_API_URL=http://localhost:8000/api/v1 AEXY_API_TOKEN=aexy_... uv run aexy-mcp
```

Then type a JSON-RPC line, for example
`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`.
