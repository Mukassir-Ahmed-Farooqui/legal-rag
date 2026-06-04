import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import func
from src.db.models import QueryLog, Document


def log_query(
    db: Session,
    user_id: uuid.UUID,
    question: str,
    answer: str | None,
    chunks_retrieved: int,
    latency_ms: int | None,
    document_id: uuid.UUID | None,
) -> QueryLog:
    """
    Log a successful query transaction to the database.
    """
    log_entry = QueryLog(
        user_id=user_id,
        document_id=document_id,
        question=question,
        answer=answer,
        chunks_retrieved=chunks_retrieved,
        latency_ms=latency_ms,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def log_auth_failure(
    db: Session,
    user_id: uuid.UUID,
    attempted_doc_id: str | None,
    reason: str,
    latency_ms: int | None,
    action: str,
) -> QueryLog:
    """
    Log an authenticated authorization failure (403) to the database.
    
    Stores attempted doc_id and failure reason in the 'question' column
    to fit the existing schema, sets 'answer' to NULL and 'chunks_retrieved' to 0.
    Resolves attempted_doc_id to the database Document's primary key id (if exists).
    """
    db_document_id = None
    if attempted_doc_id:
        try:
            attempted_uuid = uuid.UUID(attempted_doc_id)
            doc = db.query(Document).filter(Document.doc_id == attempted_uuid).first()
            if doc:
                db_document_id = doc.id
        except ValueError:
            pass

    # Construct details for the non-nullable question column
    question_content = f"403 Forbidden: {reason} | Attempted doc_id: {attempted_doc_id} | Action: {action}"

    log_entry = QueryLog(
        user_id=user_id,
        document_id=db_document_id,
        question=question_content,
        answer=None,
        chunks_retrieved=0,
        latency_ms=latency_ms,
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry


def get_recent_queries(db: Session, limit: int = 100) -> list[QueryLog]:
    """
    Retrieve recent query logs sorted by created_at descending.
    """
    return db.query(QueryLog).order_by(QueryLog.created_at.desc()).limit(limit).all()


def get_user_query_history(db: Session, user_id: uuid.UUID) -> list[QueryLog]:
    """
    Retrieve all query logs for a specific user, sorted by created_at descending.
    """
    return db.query(QueryLog).filter(QueryLog.user_id == user_id).order_by(QueryLog.created_at.desc()).all()


def get_average_latency(db: Session) -> float:
    """
    Compute the average latency of all query logs in milliseconds.
    Returns 0.0 if there are no logs.
    """
    avg_latency = db.query(func.avg(QueryLog.latency_ms)).scalar()
    return float(avg_latency) if avg_latency is not None else 0.0
