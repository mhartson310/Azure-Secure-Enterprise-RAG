from __future__ import annotations

import json
from io import StringIO
import logging

from app.telemetry import LOGGER, emit_security_event


def test_security_event_is_json_and_omits_raw_prompt_fields():
    stream = StringIO()
    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter("%(message)s"))
    LOGGER.addHandler(handler)

    try:
        emit_security_event(
            "rag_query_completed",
            correlation_id="corr-1",
            subject="user-object-id",
            tenant_id="tenant-id",
            retrieved_count=2,
            source_document_ids=["doc-1", "doc-2"],
        )
    finally:
        LOGGER.removeHandler(handler)

    event = json.loads(stream.getvalue().strip())

    assert event["event_type"] == "rag_query_completed"
    assert event["correlation_id"] == "corr-1"
    assert event["retrieved_count"] == 2
    assert event["user_hash"] != "user-object-id"
    assert event["tenant_hash"] != "tenant-id"
    assert "question" not in event
    assert "prompt" not in event
    assert "content" not in event
