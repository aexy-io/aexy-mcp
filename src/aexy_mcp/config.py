"""Configuration for the aexy-mcp bridge, from environment variables."""

import os
import sys

DEFAULT_TIMEOUT_SECONDS = 90.0


def _timeout_from(raw: str) -> float:
    """Seconds to wait for the server, or the default if the value is not a number.

    Read at import, so raising here would kill the process before ``main``
    reaches its friendly "AEXY_API_TOKEN is not set" check — and the traceback
    a client would show for ``AEXY_TIMEOUT_SECONDS=90s`` names neither the
    variable nor the fix.
    """
    try:
        seconds = float(raw)
    except ValueError:
        sys.stderr.write(
            f"aexy-mcp: AEXY_TIMEOUT_SECONDS={raw!r} is not a number; "
            f"using {DEFAULT_TIMEOUT_SECONDS:g}\n"
        )
        return DEFAULT_TIMEOUT_SECONDS
    if seconds <= 0:
        sys.stderr.write(
            f"aexy-mcp: AEXY_TIMEOUT_SECONDS={raw!r} is not positive; "
            f"using {DEFAULT_TIMEOUT_SECONDS:g}\n"
        )
        return DEFAULT_TIMEOUT_SECONDS
    return seconds


class Config:
    def __init__(self) -> None:
        self.api_url = os.environ.get("AEXY_API_URL", "http://localhost:8000/api/v1").rstrip("/")
        self.api_token = os.environ.get("AEXY_API_TOKEN", "")
        # Needed only when the token's owner belongs to more than one workspace.
        workspace_id = os.environ.get("AEXY_WORKSPACE_ID", "").strip()
        # The client recipes ship this line with a placeholder. Left as is, it
        # is not a workspace id and must not be sent as one.
        self.workspace_id = "" if workspace_id.startswith("<") else workspace_id
        self.timeout_seconds = _timeout_from(os.environ.get("AEXY_TIMEOUT_SECONDS", "90"))

    @property
    def endpoint(self) -> str:
        return f"{self.api_url}/mcp"


config = Config()
