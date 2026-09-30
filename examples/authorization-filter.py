"""
Authorization-filter example for Azure AI Search.

The important security property is not the Python syntax. It is that the filter is
constructed from trusted identity context rather than user-controlled request data.

This example validates group identifiers as UUIDs before constructing the filter.
"""

from __future__ import annotations

from typing import Iterable
from uuid import UUID


def _normalize_group_ids(group_ids: Iterable[str]) -> list[str]:
    """Return canonical UUID strings and reject malformed/untrusted identifiers."""
    normalized: list[str] = []

    for raw in group_ids:
        value = str(raw).strip()
        if not value:
            continue

        # Validation prevents callers from injecting arbitrary OData filter syntax.
        group_id = str(UUID(value))

        if group_id not in normalized:
            normalized.append(group_id)

    return normalized


def build_group_filter(trusted_group_ids: Iterable[str]) -> str:
    """
    Build a document-level security filter.

    The caller MUST supply group IDs derived from trusted Microsoft Entra identity
    context, not from a request body, query parameter, prompt, or retrieved text.
    """
    group_ids = _normalize_group_ids(trusted_group_ids)

    if not group_ids:
        # Fail closed. Returning an empty match is safer than retrieving broadly.
        return "group_ids/any(g: false)"

    joined = ",".join(group_ids)
    return f"group_ids/any(g:search.in(g, '{joined}', ','))"


def example_search(search_client, query: str, trusted_group_ids: Iterable[str]):
    """Illustrative Azure AI Search call using a mandatory authorization filter."""
    security_filter = build_group_filter(trusted_group_ids)

    return search_client.search(
        search_text=query,
        filter=security_filter,
        select=["document_id", "title", "content", "source_uri", "classification"],
        top=5,
    )


if __name__ == "__main__":
    finance_group = "11111111-1111-1111-1111-111111111111"
    engineering_group = "22222222-2222-2222-2222-222222222222"

    print(build_group_filter([finance_group]))
    print(build_group_filter([engineering_group]))
    print(build_group_filter([finance_group, engineering_group]))

    # This intentionally raises ValueError instead of allowing filter injection:
    # print(build_group_filter(["11111111-1111-1111-1111-111111111111') or true or ('"]))
