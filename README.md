# aexy-mcp

A stdio bridge to the Aexy MCP server. It holds no tools of its own: every
JSON-RPC message from your client is forwarded to `POST {AEXY_API_URL}/mcp`
with your API token, and the answer is written back. The tool list, the
permission checks, workspace policies and the audit ledger all live on the
server, so they are identical whichever way you connect.

The hosted server is `https://server.aexy.io/api/v1/mcp`. For a self-hosted
stack, substitute your own `BACKEND_URL` followed by `/api/v1/mcp`.

**You may not need this.** Clients that speak streamable HTTP — Claude Code,
Claude Desktop (via Connectors), ChatGPT — can connect to the URL directly and
sign in through the browser. Use the bridge only for clients that can just
launch a local process, or when you want to authenticate with a fixed API token
instead of a browser login.

## Claude Code

Pick one of the three. Verify with `claude mcp list`, then `/mcp` inside a
session.

**Remote, browser sign-in** (recommended — no token to manage):

```bash
claude mcp add --transport http aexy https://server.aexy.io/api/v1/mcp
```

Claude Code discovers the OAuth server from the endpoint's `WWW-Authenticate`
header and registers itself; the first `/mcp` opens a browser window to
approve the grant. The grant is bound to one workspace, so no workspace header
is needed.

**Remote, API token** (no bridge, no browser — good for CI or an agent
principal):

```bash
claude mcp add --transport http aexy https://server.aexy.io/api/v1/mcp \
  --header "Authorization: Bearer <your-api-token>"
```

Add `--header "X-Aexy-Workspace-Id: <workspace-id>"` only if the token's owner
belongs to more than one workspace.

**Local bridge with a token** (this package):

```bash
claude mcp add aexy \
  -e AEXY_API_URL=https://server.aexy.io/api/v1 \
  -e AEXY_API_TOKEN=<your-api-token> \
  -- uvx aexy-mcp@latest
```

Or commit `.mcp.json` at the repo root so everyone on the project gets it:

```json
{
  "mcpServers": {
    "aexy": {
      "command": "uvx",
      "args": ["aexy-mcp@latest"],
      "env": {
        "AEXY_API_URL": "https://server.aexy.io/api/v1",
        "AEXY_API_TOKEN": "<your-api-token>"
      }
    }
  }
}
```

Server definitions belong in `.mcp.json` (project scope) or `~/.claude.json`
(user scope). An `mcpServers` block in `settings.local.json` is ignored.

## Claude Desktop

Open **Settings → Developer → Edit config** (or edit the file directly:
`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS,
`%APPDATA%\Claude\claude_desktop_config.json` on Windows) and add:

```json
{
  "mcpServers": {
    "aexy": {
      "command": "uvx",
      "args": ["aexy-mcp@latest"],
      "env": {
        "AEXY_API_URL": "https://server.aexy.io/api/v1",
        "AEXY_API_TOKEN": "<your-api-token>",
        "AEXY_WORKSPACE_ID": "<only if you belong to more than one workspace>"
      }
    }
  }
}
```

Restart Claude Desktop. The server shows under **Developer → Local MCP
servers**; a red **Failed** badge with *"aexy-mcp was not found in the package
registry"* means `uvx` could not fetch the package — see
[Running from source](#running-from-source).

## Getting a token

Create one in Aexy under **Settings → API Tokens**. It authenticates as you and
carries only your permissions. For an unattended agent, an admin can instead
create an **agent principal** under **Settings → Agent Principals** and issue
it a token — it then acts as itself, scoped to the capabilities chosen for it,
and is already bound to a workspace.

## Environment variables

| Variable | Meaning |
| --- | --- |
| `AEXY_API_URL` | Backend API base URL, e.g. `https://server.aexy.io/api/v1` |
| `AEXY_API_TOKEN` | Your token from Settings → API Tokens, or a principal's token |
| `AEXY_WORKSPACE_ID` | Which workspace to act in. Required only when the token's owner is in several; a principal is already bound to one. An unreplaced `<placeholder>` is ignored |
| `AEXY_TIMEOUT_SECONDS` | Per-request timeout (default 90) |

## Running from source

Useful before a release is on PyPI, or to test a local change. Point `uvx` at
the checkout instead of the registry — everything else in the recipes above
stays the same:

```json
"command": "uvx",
"args": ["--from", "/path/to/mcp-server", "aexy-mcp"]
```

or, for Claude Code:

```bash
claude mcp add aexy -e AEXY_API_URL=... -e AEXY_API_TOKEN=... \
  -- uvx --from /path/to/mcp-server aexy-mcp
```

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
uv run pytest
AEXY_API_URL=http://localhost:8000/api/v1 AEXY_API_TOKEN=aexy_... uv run aexy-mcp
```

Then type a JSON-RPC line, for example
`{"jsonrpc":"2.0","id":1,"method":"tools/list"}`.

## Releasing

Publishing is automated by `.github/workflows/publish.yml` using PyPI
[trusted publishing](https://docs.pypi.org/trusted-publishers/) — no API token
is stored anywhere.

1. Bump `version` in `pyproject.toml` and add a `CHANGELOG.md` entry.
2. Commit, then tag and push the tag:

   ```bash
   git tag v1.0.1 && git push origin v1.0.1
   ```

3. The workflow runs the tests, checks that the tag matches the pyproject
   version, builds the sdist and wheel, and uploads them from the `pypi`
   GitHub environment.

One-time setup on PyPI (project owner): **Manage project → Publishing → Add a
new publisher → GitHub**, with owner `aexy-io`, repository `mcp-server`,
workflow `publish.yml`, environment `pypi`. For the very first release, add it
as a *pending publisher* from <https://pypi.org/manage/account/publishing/>
before pushing the tag, since the project does not exist yet.
