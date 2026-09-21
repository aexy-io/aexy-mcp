"""aexy-mcp — a stdio bridge to the Aexy remote MCP server.

This process holds no tools. It reads newline-delimited JSON-RPC from stdin,
forwards each message to ``POST {AEXY_API_URL}/mcp`` with the API token, and
writes whatever comes back to stdout. That is the whole program.

Why a bridge and not a server. The previous version of this package carried 27
hand-written tools with their URL paths typed out by hand — four of them called
routes that did not exist — and it authenticated against the REST API with a
personal token, which made every call look like the person at a keyboard and
skipped the governance, review gate and audit ledger the backend applies to
agents. A bridge cannot drift from the server, because it has nothing to
drift, and cannot skip the gate, because it never reaches an endpoint except
through it.

Clients that speak streamable HTTP (ChatGPT, Claude Code, Claude Desktop) do
not need this at all: point them at the same URL and they authenticate through
OAuth. This exists for clients that can only launch a process.
"""

from __future__ import annotations

import json
import sys
from typing import Any

import httpx

from .config import config


def _headers() -> dict[str, str]:
    headers = {
        "Authorization": f"Bearer {config.api_token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if config.workspace_id:
        headers["X-Aexy-Workspace-Id"] = config.workspace_id
    return headers


MAX_RELAYED_BODY_CHARS = 2000


def _clip(text: str) -> str:
    """A relayed body, short enough to read. A proxy can return a whole page."""
    text = (text or "").strip()
    if len(text) <= MAX_RELAYED_BODY_CHARS:
        return text
    return text[:MAX_RELAYED_BODY_CHARS] + f"… (+{len(text) - MAX_RELAYED_BODY_CHARS} more chars)"


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def _ids(message: Any) -> list[Any]:
    """The ids a reply would need, so a transport failure can be answered."""
    items = message if isinstance(message, list) else [message]
    return [m.get("id") for m in items if isinstance(m, dict) and "id" in m]


def forward(client: httpx.Client, line: str) -> list[dict[str, Any]]:
    """Send one stdin line to the server; return the replies to write out."""
    try:
        message = json.loads(line)
    except json.JSONDecodeError:
        return [_error(None, -32700, "Malformed JSON")]

    try:
        response = client.post(config.endpoint, content=line.encode("utf-8"), headers=_headers())
    except Exception as exc:
        # Deliberately broad. httpx.InvalidURL is not an httpx.HTTPError, so a
        # malformed AEXY_API_URL used to escape this handler and kill the
        # process mid-session, taking every pending id with it. Whatever went
        # wrong, the client is owed a reply per id it is waiting on.
        return [
            _error(rid, -32000, f"Could not reach {config.endpoint}: {exc!s} ({type(exc).__name__})")
            for rid in _ids(message)
        ]

    # Order matters. An empty body used to be read as "nothing to say" before
    # anything looked at the status, so every bodiless failure — a redirect, a
    # proxy 401, a gateway timeout — became silence, and the client sat on
    # `initialize` until its own timeout. Status first, emptiness last.
    if response.is_redirect:
        # httpx does not follow redirects by default, and following one would
        # replay a bearer token to wherever the hop points. Name the hop and
        # let the operator repoint AEXY_API_URL at it.
        location = response.headers.get("location", "(no Location header)")
        return [
            _error(
                rid,
                -32001,
                f"{response.status_code}: {config.endpoint} redirects to {location}. "
                f"Set AEXY_API_URL so it does not — an http:// URL for an https:// "
                f"server is the usual cause.",
            )
            for rid in _ids(message)
        ]

    if response.status_code >= 400:
        # The server explains itself in error_description (missing token,
        # ambiguous workspace, not a member) or FastAPI's detail (a wrong URL
        # giving 404). Relay it per request id so the client shows the words
        # rather than a bare failure — and never write a non-JSON-RPC body to
        # stdout, which a client would either ignore or choke on.
        try:
            payload = response.json()
            detail = (
                payload.get("error_description") or payload.get("detail") or response.text
                if isinstance(payload, dict)
                else response.text
            )
        except ValueError:
            detail = response.text
        # A bodiless failure still has to say something: a proxy's bare 502 is
        # the case that used to vanish.
        detail = _clip(detail) or response.reason_phrase or "no explanation given"
        code = -32001 if response.status_code in (400, 401, 403) else -32603
        return [_error(rid, code, f"{response.status_code}: {detail}") for rid in _ids(message)]

    if response.status_code == 202:
        return []  # accepted: a notification, or a batch of only notifications

    if not response.content:
        # No ids means it really was only notifications. An id means the client
        # is waiting for an answer that is never coming, so say so.
        return [
            _error(rid, -32603, f"Empty {response.status_code} from {config.endpoint}")
            for rid in _ids(message)
        ]

    try:
        body = response.json()
    except ValueError:
        return [_error(rid, -32603, f"Non-JSON response ({response.status_code}): {_clip(response.text)}") for rid in _ids(message)]
    replies = body if isinstance(body, list) else [body]
    if not all(isinstance(r, dict) and r.get("jsonrpc") == "2.0" for r in replies):
        return [_error(rid, -32603, f"Unexpected response from {config.endpoint}") for rid in _ids(message)]
    return replies


def main() -> None:
    if not config.api_token:
        sys.stderr.write("aexy-mcp: AEXY_API_TOKEN is not set\n")
        sys.exit(2)

    # A JSON-RPC line is UTF-8 by definition. Left to the locale, Windows
    # decodes it as cp1252 and a Hindi argument either mangles or raises.
    for stream in (sys.stdin, sys.stdout):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8")

    out = sys.stdout
    with httpx.Client(timeout=config.timeout_seconds) as client:
        for raw in sys.stdin:
            line = raw.strip()
            if not line:
                continue
            for reply in forward(client, line):
                out.write(json.dumps(reply, separators=(",", ":")) + "\n")
            out.flush()


if __name__ == "__main__":
    main()
