from fastapi import APIRouter, UploadFile, File, HTTPException

from src.models.responses import UploadResponse
from src.services.upload_service import ingest_uploaded_pdf

router = APIRouter()


@router.post("", response_model=UploadResponse)
def upload_document(file: UploadFile = File(...)):

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are currently supported.",
        )

    try:
        result = ingest_uploaded_pdf(file)
        return UploadResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )
