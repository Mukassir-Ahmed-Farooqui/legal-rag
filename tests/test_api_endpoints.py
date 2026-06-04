import os
import sys
import uuid
from fastapi.testclient import TestClient

# Ensure src is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app
from src.db.database import SessionLocal
from src.db.models import User, Document

client = TestClient(app)

# Generate a unique test user for the endpoint verification
_test_email = f"api_test_{uuid.uuid4().hex[:8]}@example.com"
_test_password = "TestPassword123!"

def get_auth_headers():
    # Register
    client.post("/api/v1/auth/register", json={"email": _test_email, "password": _test_password})
    # Login
    res = client.post("/api/v1/auth/login", json={"email": _test_email, "password": _test_password})
    assert res.status_code == 200
    token = res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]
    print("Root endpoint verified successfully!")


def test_health():
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert "qdrant_status" in data
    print(f"Health endpoint verified successfully! Qdrant status: {data['qdrant_status']}")


def test_query():
    headers = get_auth_headers()
    # Call query with a dummy/sample question
    response = client.post(
        "/api/v1/query",
        json={"question": "What transfer restrictions apply?", "doc_id": None},
        headers=headers
    )
    print("Query endpoint response code:", response.status_code)
    print("Query endpoint response text:", response.text)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    print("Query endpoint verified successfully!")


def test_upload():
    headers = get_auth_headers()
    # Path to sample PDF we found
    pdf_path = os.path.join(
        "data", "cuad", "CUAD_v1", "full_contract_pdf", "Part_I",
        "Affiliate_Agreements", "CreditcardscomInc_20070810_S-1_EX-10.33_362297_EX-10.33_Affiliate Agreement.pdf"
    )

    if not os.path.exists(pdf_path):
        print(f"Warning: Test PDF at {pdf_path} not found. Skipping upload test.")
        return

    print(f"Testing PDF upload with: {pdf_path}")
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test_agreement.pdf", f, "application/pdf")},
            headers=headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_agreement.pdf"
    assert data["status"] == "indexed"
    assert data["sections"] > 0
    assert data["sentences"] > 0
    print(f"Upload endpoint verified successfully! Indexed {data['sections']} sections.")


def test_documents():
    headers = get_auth_headers()
    # 1. Get current list of documents
    response = client.get("/api/v1/documents", headers=headers)
    print("GET /documents code:", response.status_code)
    assert response.status_code == 200
    initial_docs = response.json()
    assert isinstance(initial_docs, list)

    # 2. Upload a document
    pdf_path = os.path.join(
        "data", "cuad", "CUAD_v1", "full_contract_pdf", "Part_I",
        "Affiliate_Agreements", "CreditcardscomInc_20070810_S-1_EX-10.33_362297_EX-10.33_Affiliate Agreement.pdf"
    )

    if not os.path.exists(pdf_path):
        print("Warning: Test PDF not found. Skipping documents integration test.")
        return

    print("Uploading document for testing...")
    with open(pdf_path, "rb") as f:
        response = client.post(
            "/api/v1/upload",
            files={"file": ("test_agreement.pdf", f, "application/pdf")},
            headers=headers
        )
    assert response.status_code == 200
    uploaded_doc = response.json()
    doc_id = uploaded_doc["doc_id"]

    # 3. Get list of documents and check if the uploaded document is there
    response = client.get("/api/v1/documents", headers=headers)
    assert response.status_code == 200
    docs = response.json()
    assert any(d["doc_id"] == doc_id for d in docs)

    # 4. Delete the document
    response = client.delete(f"/api/v1/documents/{doc_id}", headers=headers)
    assert response.status_code == 200
    delete_res = response.json()
    assert delete_res["status"] == "deleted"
    assert delete_res["doc_id"] == doc_id

    # 5. Get list of documents and check if it's gone
    response = client.get("/api/v1/documents", headers=headers)
    assert response.status_code == 200
    docs_after = response.json()
    assert not any(d["doc_id"] == doc_id for d in docs_after)
    print("Documents endpoints verified successfully!")

    # Clean up test user & document from DB
    db = SessionLocal()
    try:
        db.query(Document).filter(Document.doc_id == uuid.UUID(doc_id)).delete()
        db.query(User).filter(User.email == _test_email).delete()
        db.commit()
    except Exception as e:
        print("API test cleanup failed:", str(e))
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("Starting API verification tests...")
    test_root()
    test_health()
    test_query()
    test_upload()
    test_documents()
    print("All tests passed successfully!")
