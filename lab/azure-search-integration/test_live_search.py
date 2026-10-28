"""Opt-in live Azure AI Search integration tests.

No actual human identities or tokens are tested: synthetic group GUIDs only.
The Azure Search admin key is a local lab credential, not a user authorization
mechanism. All tests require LIVE_AZURE_SEARCH_TESTS=1 and an endpoint/key.
"""
import os
from uuid import UUID

import pytest
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

from policy import ENGINEERING, FINANCE, allowed_ids, enforce_result_gate


pytestmark = pytest.mark.skipif(
    os.getenv("LIVE_AZURE_SEARCH_TESTS") != "1",
    reason="Live Azure tests are opt-in (LIVE_AZURE_SEARCH_TESTS=1)",
)


def _client():
    endpoint = os.environ["AZURE_SEARCH_ENDPOINT"]
    key = os.environ["AZURE_SEARCH_ADMIN_KEY"]
    index = os.getenv("AZURE_SEARCH_INDEX", "enterprise-rag-demo")
    return SearchClient(endpoint, index, AzureKeyCredential(key))


def _filter(groups):
    # Only trusted, normalized GUIDs; no raw filter fragments from user input.
    normalized = sorted({str(UUID(value)) for value in groups})
    if not normalized:
        return "group_ids/any(g: false)"
    return "group_ids/any(g:search.in(g, '" + ",".join(normalized) + "', ','))"


def _retrieve(groups, query="*"):
    return [
        dict(x)
        for x in _client().search(
            search_text=query,
            filter=_filter(groups),
            select=["document_id", "title", "content", "source_uri"],
            top=20,
        )
    ]


@pytest.mark.parametrize(
    "groups,expected",
    [
        ((FINANCE,), {"finance-001", "shared-001"}),
        ((ENGINEERING,), {"engineering-001", "shared-001"}),
        ((), set()),
    ],
)
def test_live_group_isolation(groups, expected):
    results = _retrieve(groups)
    assert {r["document_id"] for r in results} == expected
    assert {r["document_id"] for r in enforce_result_gate(results, groups)} == expected


def test_live_exact_title_does_not_bypass_acl():
    results = _retrieve((ENGINEERING,), "FY27 Finance Planning")
    assert "finance-001" not in {r["document_id"] for r in results}
    enforce_result_gate(results, (ENGINEERING,))


def test_live_cross_group_filter_is_not_supplied_by_requester():
    # A caller asking for Finance content cannot influence the trusted
    # Engineering group passed into the search filter.
    results = _retrieve((ENGINEERING,), "finance")
    assert {r["document_id"] for r in results}.issubset(allowed_ids((ENGINEERING,)))


def test_post_search_result_injection_is_rejected():
    results = _retrieve((ENGINEERING,))
    results.append({"document_id": "finance-001", "content": "injected"})
    with pytest.raises(PermissionError):
        enforce_result_gate(results, (ENGINEERING,))
