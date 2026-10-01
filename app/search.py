from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from azure.identity import DefaultAzureCredential
from azure.search.documents import SearchClient


@dataclass(frozen=True)
class RetrievedDocument:
    document_id: str
    title: str
    content: str
    source_uri: str | None
    classification: str | None


def build_group_filter(group_ids: Iterable[str]) -> str:
    normalized: list[str] = []

    for raw in group_ids:
        value = str(raw).strip()
        if not value:
            continue

        canonical = str(UUID(value))
        if canonical not in normalized:
            normalized.append(canonical)

    if not normalized:
        return "group_ids/any(g: false)"

    joined = ",".join(normalized)
    return f"group_ids/any(g:search.in(g, '{joined}', ','))"


class SecureSearch:
    def __init__(self, endpoint: str, index_name: str):
        self._client = SearchClient(
            endpoint=endpoint,
            index_name=index_name,
            credential=DefaultAzureCredential(),
        )

    def retrieve(
        self,
        question: str,
        trusted_group_ids: Iterable[str],
        top_k: int = 5,
    ) -> list[RetrievedDocument]:
        security_filter = build_group_filter(trusted_group_ids)

        results = self._client.search(
            search_text=question,
            filter=security_filter,
            select=[
                "document_id",
                "title",
                "content",
                "source_uri",
                "classification",
            ],
            top=top_k,
        )

        documents: list[RetrievedDocument] = []
        for item in results:
            documents.append(
                RetrievedDocument(
                    document_id=item["document_id"],
                    title=item["title"],
                    content=item["content"],
                    source_uri=item.get("source_uri"),
                    classification=item.get("classification"),
                )
            )

        return documents
