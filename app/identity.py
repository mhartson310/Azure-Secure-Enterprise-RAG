from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from fastapi import Header, HTTPException, status

from app.settings import Settings


GROUP_CLAIM_TYPES = {
    "groups",
    "http://schemas.microsoft.com/ws/2008/06/identity/claims/groups",
}


@dataclass(frozen=True)
class IdentityContext:
    subject: str | None
    tenant_id: str | None
    group_ids: tuple[str, ...]


def _normalize_group_ids(values: Iterable[str]) -> tuple[str, ...]:
    normalized: list[str] = []

    for raw in values:
        value = str(raw).strip()
        if not value:
            continue

        try:
            canonical = str(UUID(value))
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Identity contains an invalid group identifier.",
            ) from exc

        if canonical not in normalized:
            normalized.append(canonical)

    return tuple(normalized)


def _parse_easy_auth_principal(encoded: str) -> IdentityContext:
    try:
        padded = encoded + "=" * (-len(encoded) % 4)
        payload = base64.b64decode(padded).decode("utf-8")
        principal = json.loads(payload)
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid trusted identity header.",
        ) from exc

    claims = principal.get("claims") or []
    if not isinstance(claims, list):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Trusted identity claims are malformed.",
        )

    group_values: list[str] = []
    subject = None
    tenant_id = None

    for claim in claims:
        if not isinstance(claim, dict):
            continue

        claim_type = str(claim.get("typ", ""))
        claim_value = claim.get("val")

        if not isinstance(claim_value, str):
            continue

        if claim_type in GROUP_CLAIM_TYPES:
            group_values.append(claim_value)
        elif claim_type in {"oid", "http://schemas.microsoft.com/identity/claims/objectidentifier"}:
            subject = claim_value
        elif claim_type in {"tid", "http://schemas.microsoft.com/identity/claims/tenantid"}:
            tenant_id = claim_value

    groups = _normalize_group_ids(group_values)

    # Fail closed. A production system can add an explicit Graph-based group-overage path.
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No trusted group membership was available for authorization.",
        )

    return IdentityContext(
        subject=subject,
        tenant_id=tenant_id,
        group_ids=groups,
    )


def resolve_identity(
    settings: Settings,
    x_ms_client_principal: str | None,
    x_debug_group_ids: str | None,
) -> IdentityContext:
    if settings.identity_mode == "easy_auth":
        if not x_ms_client_principal:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Trusted authentication context is required.",
            )
        return _parse_easy_auth_principal(x_ms_client_principal)

    if not settings.allow_debug_identity:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug identity mode is disabled.",
        )

    groups = _normalize_group_ids((x_debug_group_ids or "").split(","))
    if not groups:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debug mode requires at least one valid group ID.",
        )

    return IdentityContext(
        subject="debug-user",
        tenant_id="debug-tenant",
        group_ids=groups,
    )


async def identity_dependency(
    x_ms_client_principal: str | None = Header(default=None, alias="X-MS-CLIENT-PRINCIPAL"),
    x_debug_group_ids: str | None = Header(default=None, alias="X-Debug-Group-Ids"),
) -> IdentityContext:
    # Imported lazily to avoid circular imports during testing.
    from app.main import settings

    return resolve_identity(
        settings=settings,
        x_ms_client_principal=x_ms_client_principal,
        x_debug_group_ids=x_debug_group_ids,
    )
