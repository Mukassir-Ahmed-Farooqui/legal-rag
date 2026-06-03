from fastapi.testclient import TestClient
from src.api.main import app

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
    assert response.status_code == 200
    data = response.json()
    assert "answer" in data
    assert "citations" in data
    print("Query endpoint verified successfully!")
    print(f"Answer: {data['answer'][:200]}...")


if __name__ == "__main__":
    print("Starting API verification tests...")
    test_root()
    test_health()
    test_query()
    print("All tests passed successfully!")
