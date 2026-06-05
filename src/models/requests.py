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


class ChatCreateRequest(BaseModel):
    scope_type: str = Field(..., description="Scope type: 'corpus' or 'document'")
    scope_doc_id: Optional[str] = Field(None, description="Scope document UUID string (nullable)")


class ChatRenameRequest(BaseModel):
    title: str = Field(..., description="New title of the chat session")


class ChatScopeUpdateRequest(BaseModel):
    scope_type: str = Field(..., description="Scope type: 'corpus' or 'document'")
    scope_doc_id: Optional[str] = Field(None, description="Scope document UUID string (nullable)")


class MessageCreateRequest(BaseModel):
    question: str = Field(..., description="User question to ask")
