"""Configuration for Aexy MCP server."""

import os


class Config:
    """Configuration loaded from environment variables."""

    def __init__(self):
        self.api_url = os.environ.get("AEXY_API_URL", "http://localhost:8000/api/v1")
        self.api_token = os.environ.get("AEXY_API_TOKEN", "")
        self.temporal_address = os.environ.get("TEMPORAL_ADDRESS", "localhost:7233")
        self.temporal_namespace = os.environ.get("TEMPORAL_NAMESPACE", "default")
        self.enable_temporal = os.environ.get("AEXY_ENABLE_TEMPORAL", "true").lower() == "true"


config = Config()
