from __future__ import annotations

import json
from pathlib import Path
from uuid import UUID


DATA_PATH = Path(__file__).parents[1] / "examples" / "sample-documents.json"

FINANCE = "11111111-1111-1111-1111-111111111111"
ENGINEERING = "22222222-2222-2222-2222-222222222222"


def load_documents():
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        return json.load(handle)["value"]


def authorized_documents(documents, trusted_group_ids):
    trusted = {str(UUID(value)) for value in trusted_group_ids}
    if not trusted:
        return []

    return [
        doc
        for doc in documents
        if trusted.intersection(doc.get("group_ids", []))
    ]


def ids(documents):
    return {doc["document_id"] for doc in documents}


def test_finance_user_sees_finance_and_shared_only():
    visible = authorized_documents(load_documents(), [FINANCE])
    assert ids(visible) == {"finance-001", "shared-001"}


def test_engineering_user_sees_engineering_and_shared_only():
    visible = authorized_documents(load_documents(), [ENGINEERING])
    assert ids(visible) == {"engineering-001", "shared-001"}


def test_user_with_no_groups_sees_nothing():
    assert authorized_documents(load_documents(), []) == []


def test_exact_title_does_not_bypass_acl_boundary():
    docs = authorized_documents(load_documents(), [ENGINEERING])
    matches = [d for d in docs if d["title"] == "FY27 Finance Planning"]
    assert matches == []


def test_semantic_relevance_cannot_reintroduce_unauthorized_document():
    docs = authorized_documents(load_documents(), [ENGINEERING])

    # Pretend every document gets a relevance score AFTER authorization.
    scored = sorted(
        docs,
        key=lambda d: 1 if "planning" in d["title"].lower() else 0,
        reverse=True,
    )

    assert "finance-001" not in ids(scored)


def test_cross_user_result_sets_remain_distinct():
    finance_docs = authorized_documents(load_documents(), [FINANCE])
    engineering_docs = authorized_documents(load_documents(), [ENGINEERING])

    assert "finance-001" in ids(finance_docs)
    assert "finance-001" not in ids(engineering_docs)
    assert "engineering-001" in ids(engineering_docs)
    assert "engineering-001" not in ids(finance_docs)
