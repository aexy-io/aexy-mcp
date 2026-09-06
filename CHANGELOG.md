# Changelog

All notable changes to `aexy-mcp` are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/); versions follow
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-09-06

The package is now a stdio bridge to the Aexy remote MCP server, and nothing
else. Everything it used to do itself — 35 hand-written tools, resources and
prompts calling the REST API and Temporal directly — is gone, because doing it
here meant doing it outside the application's governance: no agent actor claim,
no workspace policies, no review queue, no ledger, and four tools that called
paths which did not exist.

### Changed

- **One job.** Each line on stdin is forwarded as-is to `POST {AEXY_API_URL}/mcp`
  with the token as a bearer; each reply is written to stdout. Notifications are
  not answered; batches are forwarded intact.
- **Configuration.** `AEXY_API_URL`, `AEXY_API_TOKEN` (a personal token or an
  agent principal's), `AEXY_WORKSPACE_ID` (only when the token's owner belongs
  to more than one workspace), and optional `AEXY_TIMEOUT_SECONDS`. A
  placeholder value left in `AEXY_WORKSPACE_ID` (`<workspace-id, …>`) is
  ignored rather than sent.
- **Errors are JSON-RPC.** Every HTTP failure — an expired token, an ambiguous
  workspace, a wrong URL giving 404 — becomes a JSON-RPC error carrying the
  server's explanation and the original request id. Nothing that is not JSON-RPC
  ever reaches stdout; the one log line goes to stderr.
- **Dependencies.** `httpx` only. `mcp`, `temporalio` and the API client are
  removed.

### Removed

- All local tools, resources and prompts. The remote server offers the same
  and more (routine tools, `prompts/*`, `resources/*`), filtered to what the
  caller may reach, with every write governed and recorded.
- `AEXY_ENABLE_TEMPORAL`, `TEMPORAL_ADDRESS`, `TEMPORAL_NAMESPACE`.

## [0.1.0] - 2026-08

Initial release: a standalone MCP server calling the Aexy REST API directly.
