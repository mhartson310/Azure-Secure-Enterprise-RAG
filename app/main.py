from __future__ import annotations

from functools import lru_cache

from fastapi import Depends, FastAPI

from app.generation import GroundedGenerator
from app.identity import IdentityContext, identity_dependency
from app.models import Citation, QueryRequest, QueryResponse
from app.search import SecureSearch
from app.settings import Settings


settings = Settings.from_env()
app = FastAPI(
    title="Secure Enterprise RAG API",
    version="0.1.0",
)


@lru_cache
def get_search() -> SecureSearch:
    return SecureSearch(
        endpoint=settings.search_endpoint,
        index_name=settings.search_index,
    )


@lru_cache
def get_generator() -> GroundedGenerator:
    return GroundedGenerator(
        endpoint=settings.openai_endpoint,
        deployment=settings.openai_deployment,
        api_version=settings.openai_api_version,
    )


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(
    request: QueryRequest,
    identity: IdentityContext = Depends(identity_dependency),
) -> QueryResponse:
    documents = get_search().retrieve(
        question=request.question,
        trusted_group_ids=identity.group_ids,
        top_k=settings.top_k,
    )

    answer = get_generator().generate(
        question=request.question,
        documents=documents,
    )

    citations = [
        Citation(
            document_id=doc.document_id,
            title=doc.title,
            source_uri=doc.source_uri,
        )
        for doc in documents
    ]

    return QueryResponse(
        answer=answer,
        citations=citations,
    )
