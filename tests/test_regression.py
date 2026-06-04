import os
import sys
from fastapi.testclient import TestClient

# Ensure src is in PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.main import app

client = TestClient(app)

def test_regression_termination_citations():
    # Path to Arca agreement
    pdf_path = os.path.join(
        "data",
        "uploads",
        "ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement.pdf",
    )

    assert os.path.exists(pdf_path), f"Test PDF not found at {pdf_path}"

    # 1. Upload the PDF
    print("Uploading PDF for regression test...")
    with open(pdf_path, "rb") as f:
        res = client.post(
            "/api/v1/upload",
            files={
                "file": (
                    "ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement.pdf",
                    f,
                    "application/pdf",
                )
            },
        )
    assert res.status_code == 200
    data = res.json()
    doc_id = data["doc_id"]
    print(f"Uploaded successfully, doc_id={doc_id}")
    
    try:
        # 2. Query with the specific question
        question = "What are the termination provisions?"
        print(f"Querying: '{question}' for doc_id: {doc_id}")
        query_res = client.post(
            "/api/v1/query",
            json={"question": question, "doc_id": doc_id}
        )
        assert query_res.status_code == 200
        result = query_res.json()
        
        # Log response
        print("Answer:", result.get("answer"))
        print("Citations:", result.get("citations"))
        
        # 3. Assert citations contain "7. Duration and Termination of this Agreement"
        citations = result.get("citations", [])
        assert len(citations) > 0, "No citations returned"
        
        found_target_section = False
        target_section_name = "7. Duration and Termination of this Agreement"
        
        for citation in citations:
            section = citation.get("section", "")
            if target_section_name in section:
                found_target_section = True
                break
                
        assert found_target_section, f"Expected citation section containing '{target_section_name}' not found in: {citations}"
        print("Successfully verified termination citation in regression test!")
        
    finally:
        # Clean up
        print(f"Cleaning up uploaded document: {doc_id}")
        del_res = client.delete(f"/api/v1/documents/{doc_id}")
        assert del_res.status_code == 200
        print("Cleanup successful.")

if __name__ == "__main__":
    test_regression_termination_citations()
