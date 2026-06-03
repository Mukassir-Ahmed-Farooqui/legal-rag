from pydantic import BaseModel, Field
from typing import Optional


class QueryRequest(BaseModel):
    question: str = Field(
        ...,
        description="The question to ask the legal RAG pipeline.",
    )
    doc_id: Optional[str] = Field(
        None,
        description="Optional document ID to restrict retrieval to a specific document.",
    )
