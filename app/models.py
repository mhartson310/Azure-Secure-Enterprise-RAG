from __future__ import annotations

from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=4000)


class Citation(BaseModel):
    document_id: str
    title: str
    source_uri: str | None = None


class QueryResponse(BaseModel):
    answer: str
    citations: list[Citation]
