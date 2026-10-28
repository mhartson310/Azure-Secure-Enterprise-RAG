"""Small, fail-closed result gate for the synthetic integration lab.

This is NOT a substitute for a production authoritative ACL service.
The allowlist below is derived from the known synthetic fixture, NOT from
untrusted Search results or user-supplied group headers.
"""
from __future__ import annotations

from uuid import UUID

FINANCE = "11111111-1111-1111-1111-111111111111"
ENGINEERING = "22222222-2222-2222-2222-222222222222"

# Only synthetic lab documents. A production system needs an independent,
# trusted permission authority and a revocation/freshness strategy.
FIXTURE_ACL = {
    "finance-001": frozenset({FINANCE}),
    "engineering-001": frozenset({ENGINEERING}),
    "shared-001": frozenset({FINANCE, ENGINEERING}),
}


def allowed_ids(trusted_groups: tuple[str, ...]) -> set[str]:
    groups = {str(UUID(value)) for value in trusted_groups}
    return {
        document_id
        for document_id, acl in FIXTURE_ACL.items()
        if acl.intersection(groups)
    }


def enforce_result_gate(
    results: list[dict], trusted_groups: tuple[str, ...]
) -> list[dict]:
    """Fail closed if ANY result is outside independently defined lab ACLs."""
    allowed = allowed_ids(trusted_groups)
    for item in results:
        if item.get("document_id") not in allowed:
            raise PermissionError("Unauthorized retrieval result blocked")
    return results
