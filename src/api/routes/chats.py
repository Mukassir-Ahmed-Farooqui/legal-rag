import time
import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from src.auth import get_current_user
from src.db import get_db
from src.db.models import User, Chat, Message, Document
from src.models.requests import (
    ChatCreateRequest,
    ChatRenameRequest,
    ChatScopeUpdateRequest,
    MessageCreateRequest,
)
from src.models.responses import (
    ChatResponse,
    ChatDetailResponse,
    MessageResponse,
    StatusResponse,
    Citation,
)
from src.api.dependencies import get_rag_pipeline
from src.chain import LegalRAG
from src.services import audit_service

router = APIRouter()


@router.get("", response_model=List[ChatResponse])
def list_chats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all chat sessions owned by the current user, ordered by updated_at DESC.
    """
    try:
        chats = (
            db.query(Chat)
            .filter(Chat.user_id == current_user.id)
            .order_by(Chat.updated_at.desc())
            .all()
        )
        return [
            ChatResponse(
                id=str(c.id),
                title=c.title,
                scope_type=c.scope_type,
                scope_doc_id=str(c.scope_doc_id) if c.scope_doc_id else None,
                created_at=c.created_at.isoformat(),
                updated_at=c.updated_at.isoformat(),
            )
            for c in chats
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list chats: {str(e)}",
        )


@router.post("", response_model=ChatResponse, status_code=status.HTTP_201_CREATED)
def create_chat(
    request: ChatCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Create a new empty chat session with the specified scope.
    """
    try:
        scope_doc_uuid = None
        if request.scope_type == "document":
            if not request.scope_doc_id:
                raise HTTPException(
                    status_code=400,
                    detail="scope_doc_id is required when scope_type is 'document'.",
                )
            try:
                scope_doc_uuid = uuid.UUID(request.scope_doc_id)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid scope_doc_id format.",
                )

            # Validate document exists and is owned by the current user
            doc = (
                db.query(Document)
                .filter(Document.doc_id == scope_doc_uuid, Document.is_deleted == False)
                .first()
            )
            if not doc:
                raise HTTPException(
                    status_code=404,
                    detail="The document scoped to this chat was not found.",
                )
            if doc.owner_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Ownership denied. You do not own this document.",
                )

        new_chat = Chat(
            user_id=current_user.id,
            title="New Chat",
            scope_type=request.scope_type,
            scope_doc_id=scope_doc_uuid,
        )
        db.add(new_chat)
        db.commit()
        db.refresh(new_chat)

        return ChatResponse(
            id=str(new_chat.id),
            title=new_chat.title,
            scope_type=new_chat.scope_type,
            scope_doc_id=str(new_chat.scope_doc_id) if new_chat.scope_doc_id else None,
            created_at=new_chat.created_at.isoformat(),
            updated_at=new_chat.updated_at.isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create chat: {str(e)}",
        )


@router.get("/{chat_id}", response_model=ChatDetailResponse)
def get_chat_detail(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Load chat metadata and all sorted messages (timestamp ASC).
    """
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format.",
        )

    chat = db.query(Chat).filter(Chat.id == chat_uuid).first()
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    # Multi-tenant ownership verification
    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Ownership denied. You do not own this chat session.",
        )

    messages_resp = []
    for msg in chat.messages:
        citations_resp = None
        if msg.citations:
            citations_resp = [
                Citation(
                    document=c.get("document", ""),
                    page=c.get("page", 1),
                    section=c.get("section", ""),
                )
                for c in msg.citations
            ]
        messages_resp.append(
            MessageResponse(
                id=str(msg.id),
                role=msg.role,
                content=msg.content,
                citations=citations_resp,
                latency_ms=msg.latency_ms,
                timestamp=msg.timestamp.isoformat(),
            )
        )

    return ChatDetailResponse(
        id=str(chat.id),
        title=chat.title,
        scope_type=chat.scope_type,
        scope_doc_id=str(chat.scope_doc_id) if chat.scope_doc_id else None,
        created_at=chat.created_at.isoformat(),
        updated_at=chat.updated_at.isoformat(),
        messages=messages_resp,
    )


@router.patch("/{chat_id}", response_model=ChatResponse)
def rename_chat(
    chat_id: str,
    request: ChatRenameRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Rename the title of a chat session.
    """
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format.",
        )

    chat = db.query(Chat).filter(Chat.id == chat_uuid).first()
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Ownership denied. You do not own this chat session.",
        )

    try:
        chat.title = request.title
        chat.updated_at = func.now()
        db.commit()
        db.refresh(chat)

        return ChatResponse(
            id=str(chat.id),
            title=chat.title,
            scope_type=chat.scope_type,
            scope_doc_id=str(chat.scope_doc_id) if chat.scope_doc_id else None,
            created_at=chat.created_at.isoformat(),
            updated_at=chat.updated_at.isoformat(),
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to rename chat: {str(e)}",
        )


@router.patch("/{chat_id}/scope", response_model=ChatResponse)
def update_chat_scope(
    chat_id: str,
    request: ChatScopeUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Update the scope (type and target document) of an existing chat session.
    """
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format.",
        )

    chat = db.query(Chat).filter(Chat.id == chat_uuid).first()
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Ownership denied. You do not own this chat session.",
        )

    try:
        scope_doc_uuid = None
        if request.scope_type == "document":
            if not request.scope_doc_id:
                raise HTTPException(
                    status_code=400,
                    detail="scope_doc_id is required when scope_type is 'document'.",
                )
            try:
                scope_doc_uuid = uuid.UUID(request.scope_doc_id)
            except ValueError:
                raise HTTPException(
                    status_code=400,
                    detail="Invalid scope_doc_id format.",
                )

            # Validate document exists and is owned by the current user
            doc = (
                db.query(Document)
                .filter(Document.doc_id == scope_doc_uuid, Document.is_deleted == False)
                .first()
            )
            if not doc:
                raise HTTPException(
                    status_code=404,
                    detail="The document scoped to this chat was not found.",
                )
            if doc.owner_id != current_user.id:
                raise HTTPException(
                    status_code=403,
                    detail="Ownership denied. You do not own this document.",
                )

        chat.scope_type = request.scope_type
        chat.scope_doc_id = scope_doc_uuid
        chat.updated_at = func.now()
        db.commit()
        db.refresh(chat)

        return ChatResponse(
            id=str(chat.id),
            title=chat.title,
            scope_type=chat.scope_type,
            scope_doc_id=str(chat.scope_doc_id) if chat.scope_doc_id else None,
            created_at=chat.created_at.isoformat(),
            updated_at=chat.updated_at.isoformat(),
        )
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update chat scope: {str(e)}",
        )


@router.delete("/{chat_id}", response_model=StatusResponse)
def delete_chat(
    chat_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Delete a chat session and cascade delete all its messages.
    """
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format.",
        )

    chat = db.query(Chat).filter(Chat.id == chat_uuid).first()
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Ownership denied. You do not own this chat session.",
        )

    try:
        db.delete(chat)
        db.commit()
        return StatusResponse(
            status="success",
            message="Chat session deleted successfully.",
        )
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete chat: {str(e)}",
        )


def _format_history_block(messages: List[Message], max_chars: int = 6000) -> str:
    """
    Formats messages list into:
    User: [Question]
    Assistant: [Answer]
    Ensures the history block fits within character token constraints.
    """
    lines = []
    for msg in messages:
        role_label = "User" if msg.role == "user" else "Assistant"
        lines.append(f"{role_label}: {msg.content}")
    block = "\n".join(lines)
    return block


@router.post("/{chat_id}/messages", response_model=MessageResponse)
def create_message(
    chat_id: str,
    request: MessageCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    rag: LegalRAG = Depends(get_rag_pipeline),
):
    """
    Post a user question under a chat session, retrieve previous context turns,
    validate document scopes, run RAG, and persist user/assistant dialog turn.
    """
    start_time = time.perf_counter()
    try:
        chat_uuid = uuid.UUID(chat_id)
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail="Invalid chat_id format.",
        )

    chat = db.query(Chat).filter(Chat.id == chat_uuid).first()
    if not chat:
        raise HTTPException(
            status_code=404,
            detail="Chat session not found.",
        )

    if chat.user_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="Ownership denied. You do not own this chat session.",
        )

    allowed_doc_ids = None
    document_id_db = None

    # Scope Validation
    if chat.scope_type == "document":
        if not chat.scope_doc_id:
            raise HTTPException(
                status_code=400,
                detail="The document scoped to this chat has been deleted. Please create a new chat or switch to corpus mode.",
            )

        # Check if the document still exists and is not deleted
        doc = (
            db.query(Document)
            .filter(Document.doc_id == chat.scope_doc_id, Document.is_deleted == False)
            .first()
        )
        if not doc:
            raise HTTPException(
                status_code=400,
                detail="The document scoped to this chat has been deleted. Please create a new chat or switch to corpus mode.",
            )
        if doc.owner_id != current_user.id:
            raise HTTPException(
                status_code=403,
                detail="Ownership denied. You do not own the document scoped to this chat.",
            )

        allowed_doc_ids = str(doc.doc_id)
        document_id_db = doc.id
    else:
        # Corpus mode: retrieve all active documents owned by the user
        user_docs = (
            db.query(Document)
            .filter(Document.owner_id == current_user.id, Document.is_deleted == False)
            .all()
        )
        if not user_docs:
            # Short-circuit if user has no documents uploaded
            answer = "You have not uploaded any documents yet. Please upload a PDF before querying."
            latency_ms = int((time.perf_counter() - start_time) * 1000)

            # Transaction: Save user query and assistant response together in a transaction
            try:
                user_msg = Message(
                    chat_id=chat.id, role="user", content=request.question
                )
                db.add(user_msg)

                # Title update if this is the first question
                if chat.title == "New Chat":
                    chat.title = request.question

                chat.updated_at = func.now()
                db.flush()

                assistant_msg = Message(
                    chat_id=chat.id,
                    role="assistant",
                    content=answer,
                    citations=[],
                    latency_ms=latency_ms,
                )
                db.add(assistant_msg)
                db.commit()
                db.refresh(assistant_msg)

                # Log to query audit log
                audit_service.log_query(
                    db=db,
                    user_id=current_user.id,
                    question=request.question,
                    answer=answer,
                    chunks_retrieved=0,
                    latency_ms=latency_ms,
                    document_id=None,
                )

                return MessageResponse(
                    id=str(assistant_msg.id),
                    role=assistant_msg.role,
                    content=assistant_msg.content,
                    citations=[],
                    latency_ms=assistant_msg.latency_ms,
                    timestamp=assistant_msg.timestamp.isoformat(),
                )
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail=f"Failed to handle empty documents state transaction: {str(e)}",
                )

        allowed_doc_ids = [str(d.doc_id) for d in user_docs]

    # Save User Message & Update Title inside a single database transaction.
    # This prevents partial failures from creating orphaned chats.
    try:
        user_msg = Message(chat_id=chat.id, role="user", content=request.question)
        db.add(user_msg)

        if chat.title == "New Chat":
            chat.title = request.question

        chat.updated_at = func.now()
        db.commit()
        db.refresh(chat)
        db.refresh(user_msg)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to record message turn: {str(e)}",
        )

    # Conversational History windowing with Token Budget ceiling check.
    # Get history prior to the current user message.
    history_messages = (
        db.query(Message)
        .filter(Message.chat_id == chat.id, Message.id != user_msg.id)
        .order_by(Message.timestamp.desc())
        .limit(6)
        .all()
    )
    # The above list is in descending order (newest first). Let's reverse it to make it chronological.
    history_messages.reverse()

    chat_history_str = _format_history_block(history_messages)
    if len(chat_history_str) > 6000:
        # Fall back to trimming to the last 4 messages.
        trimmed_messages = (
            db.query(Message)
            .filter(Message.chat_id == chat.id, Message.id != user_msg.id)
            .order_by(Message.timestamp.desc())
            .limit(4)
            .all()
        )
        trimmed_messages.reverse()
        chat_history_str = _format_history_block(trimmed_messages)

    # Run LegalRAG Pipeline
    try:
        result = rag.ask(
            request.question, doc_id=allowed_doc_ids, chat_history=chat_history_str
        )
        latency_ms = int((time.perf_counter() - start_time) * 1000)

        # Save assistant message response
        assistant_msg = Message(
            chat_id=chat.id,
            role="assistant",
            content=result["answer"],
            citations=result["citations"],
            latency_ms=latency_ms,
        )
        db.add(assistant_msg)
        chat.updated_at = func.now()
        db.commit()
        db.refresh(assistant_msg)

        # Log to query audit logs
        audit_service.log_query(
            db=db,
            user_id=current_user.id,
            question=request.question,
            answer=result["answer"],
            chunks_retrieved=result["chunks_retrieved_count"],
            latency_ms=latency_ms,
            document_id=document_id_db,
        )

        citations_resp = [
            Citation(
                document=c.get("document", ""),
                page=c.get("page", 1),
                section=c.get("section", ""),
            )
            for c in result.get("citations", [])
        ]

        return MessageResponse(
            id=str(assistant_msg.id),
            role=assistant_msg.role,
            content=assistant_msg.content,
            citations=citations_resp,
            latency_ms=assistant_msg.latency_ms,
            timestamp=assistant_msg.timestamp.isoformat(),
        )

    except Exception as e:
        # If RAG fails, user message remains committed (as per plan), but we report 500 error.
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while generating RAG response: {str(e)}",
        )
