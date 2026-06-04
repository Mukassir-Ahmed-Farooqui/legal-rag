import os
import sys
import uuid
import pytest
from fastapi.testclient import TestClient

# Ensure src is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app
from src.db.database import SessionLocal
from src.db.models import User, Document, QueryLog
from src.services import audit_service

client = TestClient(app)

def test_audit_logging_lifecycle():
    pdf_path = os.path.join("data", "uploads", "test_agreement.pdf")
    if not os.path.exists(pdf_path):
        print(f"Warning: test PDF at {pdf_path} not found. Skipping audit logging tests.")
        return

    # Clear previous query logs to ensure count accuracy
    db = SessionLocal()
    try:
        db.query(QueryLog).delete()
        db.commit()
    finally:
        db.close()

    # 1. Register & Login User A
    email_a = f"audit_a_{uuid.uuid4().hex[:8]}@example.com"
    pw_a = "Password123!"
    
    assert client.post("/api/v1/auth/register", json={"email": email_a, "password": pw_a}).status_code == 201
    res_login_a = client.post("/api/v1/auth/login", json={"email": email_a, "password": pw_a})
    assert res_login_a.status_code == 200
    token_a = res_login_a.json()["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 2. Register & Login User B
    email_b = f"audit_b_{uuid.uuid4().hex[:8]}@example.com"
    pw_b = "Password123!"
    
    assert client.post("/api/v1/auth/register", json={"email": email_b, "password": pw_b}).status_code == 201
    res_login_b = client.post("/api/v1/auth/login", json={"email": email_b, "password": pw_b})
    assert res_login_b.status_code == 200
    token_b = res_login_b.json()["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    db = SessionLocal()
    try:
        user_a = db.query(User).filter(User.email == email_a).first()
        user_b = db.query(User).filter(User.email == email_b).first()
        user_a_id = user_a.id
        user_b_id = user_b.id
    finally:
        db.close()

    doc_id_a = None
    db_doc_id_a = None

    try:
        # 3. User A uploads a document
        print("User A uploading a document...")
        with open(pdf_path, "rb") as f:
            res_upload = client.post(
                "/api/v1/upload",
                files={"file": ("agreement_audit.pdf", f, "application/pdf")},
                headers=headers_a
            )
        assert res_upload.status_code == 200
        doc_id_a = res_upload.json()["doc_id"]

        # Fetch database Document.id (primary key UUID)
        db = SessionLocal()
        try:
            doc_a = db.query(Document).filter(Document.doc_id == uuid.UUID(doc_id_a)).first()
            assert doc_a is not None
            db_doc_id_a = doc_a.id
        finally:
            db.close()

        # 4. Successful document-specific query logged
        print("Testing successful document-specific query...")
        question_1 = "What is the referral fee?"
        res_q1 = client.post(
            "/api/v1/query",
            json={"question": question_1, "doc_id": doc_id_a},
            headers=headers_a
        )
        assert res_q1.status_code == 200

        # Check DB log
        db = SessionLocal()
        try:
            logs = db.query(QueryLog).filter(QueryLog.user_id == user_a_id).all()
            assert len(logs) == 1
            log = logs[0]
            assert log.question == question_1
            assert log.answer is not None
            assert len(log.answer) > 0
            assert log.document_id == db_doc_id_a  # Must map to the database primary key ID
            assert log.chunks_retrieved > 0
            assert log.latency_ms is not None and log.latency_ms >= 0
        finally:
            db.close()

        # 5. Successful corpus-wide query logged (document_id = NULL)
        print("Testing corpus-wide query...")
        question_2 = "Who are the parties to this agreement?"
        res_q2 = client.post(
            "/api/v1/query",
            json={"question": question_2},
            headers=headers_a
        )
        assert res_q2.status_code == 200

        # Check DB logs
        db = SessionLocal()
        try:
            logs = db.query(QueryLog).filter(QueryLog.user_id == user_a_id).order_by(QueryLog.created_at.asc()).all()
            assert len(logs) == 2
            log2 = logs[1]
            assert log2.question == question_2
            assert log2.document_id is None  # Corpus query must have NULL document_id
            assert log2.chunks_retrieved > 0
            assert log2.latency_ms is not None and log2.latency_ms >= 0
        finally:
            db.close()

        # 6. 403 Authorization Failure logged (Query Access Denied)
        print("Testing unauthorized query attempt (403)...")
        res_q_unauth = client.post(
            "/api/v1/query",
            json={"question": "What is the referral fee?", "doc_id": doc_id_a},
            headers=headers_b
        )
        assert res_q_unauth.status_code == 403

        # Check DB logs for User B
        db = SessionLocal()
        try:
            logs_b = db.query(QueryLog).filter(QueryLog.user_id == user_b_id).all()
            assert len(logs_b) == 1
            log_b = logs_b[0]
            assert "403 Forbidden" in log_b.question
            assert "Attempted doc_id" in log_b.question
            assert log_b.document_id == db_doc_id_a  # Resolves correctly
            assert log_b.answer is None  # Answer must be NULL
            assert log_b.chunks_retrieved == 0  # Chunks retrieved must be 0
            assert log_b.latency_ms is not None and log_b.latency_ms >= 0
        finally:
            db.close()

        # 7. 403 Authorization Failure logged (Delete Access Denied)
        print("Testing unauthorized delete attempt (403)...")
        res_del_unauth = client.delete(
            f"/api/v1/documents/{doc_id_a}",
            headers=headers_b
        )
        assert res_del_unauth.status_code == 403

        # Check DB logs for User B
        db = SessionLocal()
        try:
            logs_b2 = db.query(QueryLog).filter(QueryLog.user_id == user_b_id).order_by(QueryLog.created_at.asc()).all()
            assert len(logs_b2) == 2
            log_b2 = logs_b2[1]
            assert "DELETE" in log_b2.question
            assert "403 Forbidden" in log_b2.question
            assert log_b2.document_id == db_doc_id_a
            assert log_b2.answer is None
            assert log_b2.chunks_retrieved == 0
            assert log_b2.latency_ms is not None and log_b2.latency_ms >= 0
        finally:
            db.close()

        # 8. 401 Request NOT logged
        print("Testing 401 Request not logged...")
        res_q_401 = client.post(
            "/api/v1/query",
            json={"question": "What is the referral fee?", "doc_id": doc_id_a},
            headers={"Authorization": "Bearer invalid_token_xyz"}
        )
        assert res_q_401.status_code == 401

        # Check total logs in DB
        db = SessionLocal()
        try:
            total_logs = db.query(QueryLog).count()
            # We expect exactly 4 logs (2 for User A success, 1 for User B query fail, 1 for User B delete fail)
            assert total_logs == 4
        finally:
            db.close()

        # 9. Verify Service helper utilities
        print("Testing admin audit utilities...")
        db = SessionLocal()
        try:
            # get_recent_queries
            recent = audit_service.get_recent_queries(db, limit=10)
            assert len(recent) == 4
            
            # get_user_query_history
            history_a = audit_service.get_user_query_history(db, user_a_id)
            assert len(history_a) == 2
            assert history_a[0].question == question_2
            assert history_a[1].question == question_1

            history_b = audit_service.get_user_query_history(db, user_b_id)
            assert len(history_b) == 2

            # get_average_latency
            avg_latency = audit_service.get_average_latency(db)
            assert avg_latency >= 0.0
            print(f"Average latency computed: {avg_latency} ms")
        finally:
            db.close()

        # 10. User A deletes own document (verifying successful delete does not create a QueryLog)
        print("User A deleting own document...")
        res_del_auth = client.delete(
            f"/api/v1/documents/{doc_id_a}",
            headers=headers_a
        )
        assert res_del_auth.status_code == 200

        # Check total logs in DB (should still be 4)
        db = SessionLocal()
        try:
            total_logs_final = db.query(QueryLog).count()
            assert total_logs_final == 4
            print("Successfully verified query count accuracy: exactly 1 log per query request and no duplicate rows!")
        finally:
            db.close()

    finally:
        # Clean up database records
        db = SessionLocal()
        try:
            db.query(QueryLog).delete()
            if doc_id_a:
                db.query(Document).filter(Document.doc_id == uuid.UUID(doc_id_a)).delete()
            db.query(User).filter(User.id == user_a_id).delete()
            db.query(User).filter(User.id == user_b_id).delete()
            db.commit()
        except Exception as e:
            print("DB Cleanup failed:", str(e))
            db.rollback()
        finally:
            db.close()

if __name__ == "__main__":
    print("Running audit logging lifecycle integration tests...")
    test_audit_logging_lifecycle()
    print("Audit logging lifecycle integration tests passed successfully!")
