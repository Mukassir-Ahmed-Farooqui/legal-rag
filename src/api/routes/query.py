from fastapi import APIRouter, Depends, HTTPException
from src.api.dependencies import get_rag_pipeline
from src.chain import LegalRAG
from src.models.requests import QueryRequest
from src.models.responses import QueryResponse

router = APIRouter()


@router.post("", response_model=QueryResponse)
def query_rag(
    request: QueryRequest,
    rag: LegalRAG = Depends(get_rag_pipeline),
) -> QueryResponse:
    """
    Query the legal RAG pipeline with a specific question.
    Optionally restrict search to a specific document ID.
    """
    try:
        result = rag.ask(request.question, doc_id=request.doc_id)
        return QueryResponse(
            answer=result["answer"],
            citations=result["citations"],
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing the request: {str(e)}",
        )

