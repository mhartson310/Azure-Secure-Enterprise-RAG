from __future__ import annotations

import hashlib
import json
import logging
from datetime import datetime, timezone
from typing import Any


LOGGER = logging.getLogger("rag_security")
LOGGER.setLevel(logging.INFO)

if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)

LOGGER.propagate = False


def _pseudonymize(value: str | None) -> str | None:
    if not value:
        return None
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def emit_security_event(
    event_type: str,
    *,
    correlation_id: str,
    subject: str | None = None,
    tenant_id: str | None = None,
    outcome: str = "success",
    **fields: Any,
) -> None:
    """
    Emit a single-line structured JSON event for Azure Container Apps / Log Analytics.

    Privacy rules:
    - never log prompts or retrieved document content;
    - pseudonymize user/tenant identifiers by default;
    - keep event fields operational and security-focused.
    """
    event = {
        "schema_version": "1.0",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        "outcome": outcome,
        "correlation_id": correlation_id,
        "user_hash": _pseudonymize(subject),
        "tenant_hash": _pseudonymize(tenant_id),
        **fields,
    }

    LOGGER.info(json.dumps(event, separators=(",", ":"), default=str))
