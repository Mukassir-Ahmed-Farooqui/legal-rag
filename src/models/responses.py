from pydantic import BaseModel, Field
from typing import List, Optional


class Citation(BaseModel):
    document: str = Field(..., description="The filename of the source document.")
    page: int = Field(..., description="The page number of the source document.")
    section: str = Field(..., description="The section heading of the citation.")


class QueryResponse(BaseModel):
    answer: str = Field(
        ...,
        description="The generated answer from the legal RAG model.",
    )
    citations: List[Citation] = Field(
        default_factory=list,
        description="The source citations used to answer the question.",
    )


class HealthResponse(BaseModel):
    status: str = Field(..., description="Overall API service health status.")
    version: str = Field(..., description="API software version.")
    qdrant_status: str = Field(
        ...,
        description="Connectivity status to the Qdrant vector database.",
    )


class UploadResponse(BaseModel):
    doc_id: str
    filename: str
    sections: int
    sentences: int
    status: str

