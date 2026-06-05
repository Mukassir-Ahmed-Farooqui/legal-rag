import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure src is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app
from src.db.database import SessionLocal
from src.db.models import User, Document, Chat, Message

client = TestClient(app)


def create_test_user(email: str, password: str = "TestPassword123!"):
    # Register
    client.post("/api/v1/auth/register", json={"email": email, "password": password})
    # Login
    res = client.post("/api/v1/auth/login", json={"email": email, "password": password})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def cleanup_user(email: str):
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        if user:
            # Cascading deletes chats and query logs
            db.delete(user)
            db.commit()
    except Exception as e:
        print(f"Cleanup failed for user {email}: {e}")
        db.rollback()
    finally:
        db.close()


def test_chat_lifecycle_and_isolation():
    user_a_email = f"user_a_{uuid.uuid4().hex[:8]}@example.com"
    user_b_email = f"user_b_{uuid.uuid4().hex[:8]}@example.com"

    headers_a = create_test_user(user_a_email)
    headers_b = create_test_user(user_b_email)

    try:
        # 1. User A creates a chat session
        create_res = client.post(
            "/api/v1/chats",
            json={"scope_type": "corpus", "scope_doc_id": None},
            headers=headers_a,
        )
        assert create_res.status_code == 201
        chat_id_a = create_res.json()["id"]
        assert create_res.json()["title"] == "New Chat"

        # 2. Verify User B cannot view User A's chat (Multi-tenant check)
        get_res = client.get(f"/api/v1/chats/{chat_id_a}", headers=headers_b)
        assert get_res.status_code == 403

        # 3. Verify User B cannot rename User A's chat
        rename_res = client.patch(
            f"/api/v1/chats/{chat_id_a}",
            json={"title": "Hacked Title"},
            headers=headers_b,
        )
        assert rename_res.status_code == 403

        # 4. Verify User B cannot post message to User A's chat
        msg_res = client.post(
            f"/api/v1/chats/{chat_id_a}/messages",
            json={"question": "Should fail"},
            headers=headers_b,
        )
        assert msg_res.status_code == 403

        # 5. Verify User B cannot delete User A's chat
        del_res = client.delete(f"/api/v1/chats/{chat_id_a}", headers=headers_b)
        assert del_res.status_code == 403

        # 6. User A lists chats
        list_res = client.get("/api/v1/chats", headers=headers_a)
        assert list_res.status_code == 200
        assert any(c["id"] == chat_id_a for c in list_res.json())

        # 7. User B lists chats (should not see User A's chat)
        list_b_res = client.get("/api/v1/chats", headers=headers_b)
        assert list_b_res.status_code == 200
        assert not any(c["id"] == chat_id_a for c in list_b_res.json())

        # 8. User A renames the chat
        rename_ok_res = client.patch(
            f"/api/v1/chats/{chat_id_a}",
            json={"title": "Updated Session Title"},
            headers=headers_a,
        )
        assert rename_ok_res.status_code == 200
        assert rename_ok_res.json()["title"] == "Updated Session Title"

        # 9. User A deletes the chat
        del_ok_res = client.delete(f"/api/v1/chats/{chat_id_a}", headers=headers_a)
        assert del_ok_res.status_code == 200
        assert del_ok_res.json()["status"] == "success"

        # 10. User A verifies it is deleted
        get_deleted_res = client.get(f"/api/v1/chats/{chat_id_a}", headers=headers_a)
        assert get_deleted_res.status_code == 404

    finally:
        cleanup_user(user_a_email)
        cleanup_user(user_b_email)


def test_first_question_title_generation():
    email = f"user_title_{uuid.uuid4().hex[:8]}@example.com"
    headers = create_test_user(email)

    try:
        # Create chat
        create_res = client.post(
            "/api/v1/chats",
            json={"scope_type": "corpus", "scope_doc_id": None},
            headers=headers,
        )
        chat_id = create_res.json()["id"]

        # Post first message. (If no documents uploaded, RAG fallback returns standard message immediately but still saves)
        question = "What is the liability cap under this agreement?"
        msg_res = client.post(
            f"/api/v1/chats/{chat_id}/messages",
            json={"question": question},
            headers=headers,
        )
        assert msg_res.status_code == 200

        # Load chat details and verify title became the full question text without database truncation
        detail_res = client.get(f"/api/v1/chats/{chat_id}", headers=headers)
        assert detail_res.status_code == 200
        assert detail_res.json()["title"] == question

    finally:
        cleanup_user(email)


def test_scope_validation_and_deletion_cascading():
    email = f"user_scope_{uuid.uuid4().hex[:8]}@example.com"
    headers = create_test_user(email)

    db = SessionLocal()
    try:
        # Create document directly in DB linked to user
        user = db.query(User).filter(User.email == email).first()
        doc_uuid = uuid.uuid4()
        test_doc = Document(
            doc_id=doc_uuid,
            owner_id=user.id,
            filename="scope_test_doc.pdf",
            chunk_count=1,
            is_deleted=False,
        )
        db.add(test_doc)
        db.commit()
        db.refresh(test_doc)

        # Create chat scoped to this document
        create_res = client.post(
            "/api/v1/chats",
            json={"scope_type": "document", "scope_doc_id": str(doc_uuid)},
            headers=headers,
        )
        assert create_res.status_code == 201
        chat_id = create_res.json()["id"]
        assert create_res.json()["scope_doc_id"] == str(doc_uuid)

        # Update document to deleted (simulate document deletion)
        test_doc.is_deleted = True
        db.commit()

        # Try posting a message. It should return 400 with a clear message
        msg_res = client.post(
            f"/api/v1/chats/{chat_id}/messages",
            json={"question": "What is the termination period?"},
            headers=headers,
        )
        assert msg_res.status_code == 400
        assert "The document scoped to this chat has been deleted" in msg_res.json()["detail"]

        # Test cascading at DB level by physically deleting document row
        # In a real situation, `doc_id` references will be set to NULL (ondelete="SET NULL")
        db.delete(test_doc)
        db.commit()

        # Load chat metadata
        detail_res = client.get(f"/api/v1/chats/{chat_id}", headers=headers)
        assert detail_res.status_code == 200
        # Verify scope_doc_id is now NULL (set to None)
        assert detail_res.json()["scope_doc_id"] is None

    finally:
        db.close()
        cleanup_user(email)


def test_token_budget_context_window():
    email = f"user_token_{uuid.uuid4().hex[:8]}@example.com"
    headers = create_test_user(email)

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == email).first()
        # Create chat
        chat = Chat(user_id=user.id, title="Token Budget Chat", scope_type="corpus")
        db.add(chat)
        db.commit()
        db.refresh(chat)

        # Let's populate 6 long messages (alternating roles)
        # 1 user message + 1 assistant message is 1 turn. We need 3 turns.
        long_content_user = "A " * 2000  # 4000 characters
        long_content_assistant = "B " * 2000  # 4000 characters
        # Total characters will far exceed 6000 character limit

        for i in range(3):
            msg_u = Message(chat_id=chat.id, role="user", content=f"Q{i}: {long_content_user[:1000]}")
            msg_a = Message(chat_id=chat.id, role="assistant", content=f"A{i}: {long_content_assistant[:1000]}")
            db.add(msg_u)
            db.add(msg_a)
        
        # Add the current user query message
        curr_msg = Message(chat_id=chat.id, role="user", content="Show budget fallback")
        db.add(curr_msg)
        db.commit()

        # Let's call the helper format history method directly
        from src.api.routes.chats import _format_history_block

        # Query messages for the chat excluding current one
        history_messages = (
            db.query(Message)
            .filter(Message.chat_id == chat.id, Message.id != curr_msg.id)
            .order_by(Message.timestamp.desc())
            .limit(6)
            .all()
        )
        history_messages.reverse()
        
        chat_history_str = _format_history_block(history_messages)
        # Length of 6 messages: each has 1000 chars, so ~6000+ chars
        assert len(chat_history_str) > 6000

        # Verify fallback logic: trim to 4 messages instead
        trimmed_messages = (
            db.query(Message)
            .filter(Message.chat_id == chat.id, Message.id != curr_msg.id)
            .order_by(Message.timestamp.desc())
            .limit(4)
            .all()
        )
        trimmed_messages.reverse()
        trimmed_chat_history_str = _format_history_block(trimmed_messages)
        assert len(trimmed_chat_history_str) <= 6000  # Fits within token limit

    finally:
        db.close()
        cleanup_user(email)
