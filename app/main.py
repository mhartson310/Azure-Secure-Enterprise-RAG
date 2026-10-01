from __future__ import annotations

from functools import lru_cache
from uuid import uuid4

from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse

from app.generation import GroundedGenerator
from app.identity import IdentityContext, identity_dependency
from app.models import Citation, QueryRequest, QueryResponse
from app.search import SecureSearch
from app.settings import Settings
from app.telemetry import emit_security_event


settings = Settings.from_env()
app = FastAPI(
    title="Secure Enterprise RAG API",
    version="0.2.0",
)


@app.middleware("http")
async def correlation_middleware(request: Request, call_next):
    correlation_id = request.headers.get("X-Correlation-ID") or str(uuid4())
    request.state.correlation_id = correlation_id

    try:
        response = await call_next(request)
    except Exception:
        emit_security_event(
            "rag_request_failed",
            correlation_id=correlation_id,
            outcome="error",
            path=request.url.path,
            method=request.method,
        )
        raise

    response.headers["X-Correlation-ID"] = correlation_id
    return response


@app.exception_handler(HTTPException)
async def security_http_exception_handler(request: Request, exc: HTTPException):
    correlation_id = getattr(request.state, "correlation_id", str(uuid4()))

    if exc.status_code in {401, 403}:
        emit_security_event(
            "rag_authorization_denied",
            correlation_id=correlation_id,
            outcome="denied",
            status_code=exc.status_code,
            reason=str(exc.detail),
            path=request.url.path,
        )

    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers={"X-Correlation-ID": correlation_id},
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
    http_request: Request,
    identity: IdentityContext = Depends(identity_dependency),
) -> QueryResponse:
    correlation_id = getattr(http_request.state, "correlation_id", str(uuid4()))

    emit_security_event(
        "rag_query_started",
        correlation_id=correlation_id,
        subject=identity.subject,
        tenant_id=identity.tenant_id,
        group_count=len(identity.group_ids),
        search_index=settings.search_index,
    )

    documents = get_search().retrieve(
        question=request.question,
        trusted_group_ids=identity.group_ids,
        top_k=settings.top_k,
    )

    if not documents:
        emit_security_event(
            "rag_no_authorized_context",
            correlation_id=correlation_id,
            subject=identity.subject,
            tenant_id=identity.tenant_id,
            outcome="no_results",
            retrieved_count=0,
            search_index=settings.search_index,
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

    emit_security_event(
        "rag_query_completed",
        correlation_id=correlation_id,
        subject=identity.subject,
        tenant_id=identity.tenant_id,
        retrieved_count=len(documents),
        source_document_ids=[doc.document_id for doc in documents],
        search_index=settings.search_index,
        model_deployment=settings.openai_deployment,
    )

    return QueryResponse(
        answer=answer,
        citations=citations,
    )
