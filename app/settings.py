from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    search_endpoint: str
    search_index: str
    openai_endpoint: str
    openai_deployment: str
    openai_api_version: str
    identity_mode: str
    allow_debug_identity: bool
    top_k: int

    @classmethod
    def from_env(cls) -> "Settings":
        identity_mode = os.getenv("IDENTITY_MODE", "easy_auth").strip().lower()
        if identity_mode not in {"easy_auth", "debug"}:
            raise RuntimeError("IDENTITY_MODE must be 'easy_auth' or 'debug'.")

        return cls(
            search_endpoint=os.environ["AZURE_SEARCH_ENDPOINT"],
            search_index=os.getenv("AZURE_SEARCH_INDEX", "enterprise-rag-demo"),
            openai_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
            openai_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT"],
            openai_api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
            identity_mode=identity_mode,
            allow_debug_identity=os.getenv("ALLOW_DEBUG_IDENTITY", "false").lower() == "true",
            top_k=int(os.getenv("SEARCH_TOP_K", "5")),
        )
