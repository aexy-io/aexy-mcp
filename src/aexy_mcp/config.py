"""Configuration for the aexy-mcp bridge, from environment variables."""

import os


class Config:
    def __init__(self) -> None:
        self.api_url = os.environ.get("AEXY_API_URL", "http://localhost:8000/api/v1").rstrip("/")
        self.api_token = os.environ.get("AEXY_API_TOKEN", "")
        # Needed only when the token's owner belongs to more than one workspace.
        workspace_id = os.environ.get("AEXY_WORKSPACE_ID", "").strip()
        # The client recipes ship this line with a placeholder. Left as is, it
        # is not a workspace id and must not be sent as one.
        self.workspace_id = "" if workspace_id.startswith("<") else workspace_id
        self.timeout_seconds = float(os.environ.get("AEXY_TIMEOUT_SECONDS", "90"))

    @property
    def endpoint(self) -> str:
        return f"{self.api_url}/mcp"


config = Config()
