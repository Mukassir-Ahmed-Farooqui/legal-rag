from fastapi import APIRouter, HTTPException

from src.services.document_service import (
    list_documents,
    delete_document,
)

router = APIRouter()


@router.get("")
def get_documents():

    try:
        return list_documents()

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{doc_id}")
def remove_document(doc_id: str):

    try:
        return delete_document(doc_id)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
