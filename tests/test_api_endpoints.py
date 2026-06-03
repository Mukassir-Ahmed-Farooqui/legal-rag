from fastapi.testclient import TestClient
from src.api.main import app
import os

client = TestClient(app)


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
    # Call query with a dummy/sample question
    response = client.post(
        "/api/v1/query",
        json={"question": "What transfer restrictions apply?", "doc_id": None},
    )
    print("Query endpoint response code:", response.status_code)
    print("Query endpoint response text:", response.text)
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    print("Query endpoint verified successfully!")
    print(f"Answer: {data['answer'][:200]}...")


def test_upload():
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
            files={"file": ("test_agreement.pdf", f, "application/pdf")}
        )

    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test_agreement.pdf"
    assert data["status"] == "indexed"
    assert data["sections"] > 0
    assert data["sentences"] > 0
    print(f"Upload endpoint verified successfully! Indexed {data['sections']} sections and {data['sentences']} sentences.")


if __name__ == "__main__":
    print("Starting API verification tests...")
    test_root()
    test_health()
    test_query()
    test_upload()
    print("All tests passed successfully!")
