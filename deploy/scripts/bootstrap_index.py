from __future__ import annotations

import json
import os
from pathlib import Path

from azure.core.credentials import AzureKeyCredential
from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchField,
    SearchFieldDataType,
    SearchIndex,
)


ROOT = Path(__file__).resolve().parents[2]
SAMPLE_DOCUMENTS = ROOT / "examples" / "sample-documents.json"
INDEX_NAME = os.getenv("AZURE_SEARCH_INDEX", "enterprise-rag-demo")
SEARCH_ENDPOINT = os.environ["AZURE_SEARCH_ENDPOINT"]


def credential():
    """
    Prefer Microsoft Entra ID through DefaultAzureCredential.

    AZURE_SEARCH_ADMIN_KEY is supported only as a lab/bootstrap fallback. Production
    workloads should use managed identity / Entra RBAC wherever possible.
    """
    admin_key = os.getenv("AZURE_SEARCH_ADMIN_KEY")
    if admin_key:
        return AzureKeyCredential(admin_key)

    return DefaultAzureCredential(exclude_interactive_browser_credential=False)


def build_index() -> SearchIndex:
    return SearchIndex(
        name=INDEX_NAME,
        fields=[
            SearchField(
                name="document_id",
                type=SearchFieldDataType.String,
                key=True,
                filterable=True,
            ),
            SearchField(
                name="title",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="content",
                type=SearchFieldDataType.String,
                searchable=True,
            ),
            SearchField(
                name="source_uri",
                type=SearchFieldDataType.String,
                retrievable=True,
            ),
            SearchField(
                name="classification",
                type=SearchFieldDataType.String,
                filterable=True,
                facetable=True,
                retrievable=True,
            ),
            SearchField(
                name="group_ids",
                type=SearchFieldDataType.Collection(SearchFieldDataType.String),
                filterable=True,
                retrievable=False,
            ),
        ],
    )


def load_documents() -> list[dict]:
    payload = json.loads(SAMPLE_DOCUMENTS.read_text(encoding="utf-8"))
    documents = payload["value"]

    # The REST sample includes @search.action; upload_documents doesn't need it.
    for document in documents:
        document.pop("@search.action", None)

    return documents


def main() -> None:
    cred = credential()

    index_client = SearchIndexClient(
        endpoint=SEARCH_ENDPOINT,
        credential=cred,
    )
    index_client.create_or_update_index(build_index())

    search_client = SearchClient(
        endpoint=SEARCH_ENDPOINT,
        index_name=INDEX_NAME,
        credential=cred,
    )

    results = search_client.upload_documents(load_documents())
    failed = [result for result in results if not result.succeeded]

    if failed:
        for result in failed:
            print(f"FAILED: {result.key}: {result.error_message}")
        raise SystemExit(1)

    print(f"Created/updated index: {INDEX_NAME}")
    print(f"Uploaded {len(results)} sample documents.")
    print("Next: run the retrieval tests with trusted group IDs.")


if __name__ == "__main__":
    main()
