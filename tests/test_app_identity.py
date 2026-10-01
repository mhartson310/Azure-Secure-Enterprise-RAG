from __future__ import annotations

import base64
import json

import pytest
from fastapi import HTTPException

from app.identity import resolve_identity
from app.settings import Settings


FINANCE = "11111111-1111-1111-1111-111111111111"


def settings(identity_mode: str, allow_debug_identity: bool = False) -> Settings:
    return Settings(
        search_endpoint="https://example.search.windows.net",
        search_index="enterprise-rag-demo",
        openai_endpoint="https://example.openai.azure.com/",
        openai_deployment="demo",
        openai_api_version="2024-10-21",
        identity_mode=identity_mode,
        allow_debug_identity=allow_debug_identity,
        top_k=5,
    )


def encode_principal(claims):
    payload = json.dumps({"claims": claims}).encode("utf-8")
    return base64.b64encode(payload).decode("utf-8")


def test_easy_auth_extracts_trusted_groups():
    encoded = encode_principal(
        [
            {"typ": "groups", "val": FINANCE},
            {"typ": "oid", "val": "user-1"},
            {"typ": "tid", "val": "tenant-1"},
        ]
    )

    identity = resolve_identity(settings("easy_auth"), encoded, None)
    assert identity.group_ids == (FINANCE,)
    assert identity.subject == "user-1"


def test_easy_auth_fails_closed_without_header():
    with pytest.raises(HTTPException) as exc:
        resolve_identity(settings("easy_auth"), None, None)

    assert exc.value.status_code == 401


def test_easy_auth_fails_closed_without_groups():
    encoded = encode_principal([{"typ": "oid", "val": "user-1"}])

    with pytest.raises(HTTPException) as exc:
        resolve_identity(settings("easy_auth"), encoded, None)

    assert exc.value.status_code == 403


def test_debug_identity_requires_explicit_enablement():
    with pytest.raises(HTTPException) as exc:
        resolve_identity(settings("debug", False), None, FINANCE)

    assert exc.value.status_code == 403


def test_debug_identity_accepts_valid_guid_when_enabled():
    identity = resolve_identity(settings("debug", True), None, FINANCE)
    assert identity.group_ids == (FINANCE,)
