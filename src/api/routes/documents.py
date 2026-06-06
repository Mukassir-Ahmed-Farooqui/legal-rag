import time
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from src.services.document_service import (
    list_documents,
    delete_document,
)
from src.auth.dependencies import get_current_user
from src.db.database import get_db
from src.db.models import User
from src.services import audit_service

router = APIRouter()


@router.get("")
def get_documents(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        return list_documents(db=db, user_id=current_user.id)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )


@router.delete("/{doc_id}")
def remove_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    start_time = time.perf_counter()
    try:
        return delete_document(db=db, doc_id=doc_id, user_id=current_user.id)
    except HTTPException as he:
        if he.status_code == 403:
            latency_ms = int((time.perf_counter() - start_time) * 1000)
            audit_service.log_auth_failure(
                db=db,
                user_id=current_user.id,
                attempted_doc_id=doc_id,
                reason=he.detail,
                latency_ms=latency_ms,
                action="DELETE",
            )
        raise he
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

from fastapi.responses import FileResponse
from pathlib import Path
import uuid
from src.db.models import Document

@router.get("/{doc_id}/download")
def download_document(
    doc_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    try:
        doc_uuid = uuid.UUID(doc_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid doc_id format.")

    doc = db.query(Document).filter(
        Document.doc_id == doc_uuid,
        Document.is_deleted == False
    ).first()

    if not doc:
        raise HTTPException(status_code=404, detail="Document not found.")

    if doc.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied.")

    file_path = Path("data/uploads") / doc.filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File physically missing on server.")

    return FileResponse(
        path=file_path,
        filename=doc.filename,
        media_type=doc.content_type or "application/pdf"
    )
