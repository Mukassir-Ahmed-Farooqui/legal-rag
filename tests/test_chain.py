import pytest
from src.chain import LegalRAG

@pytest.mark.skip(reason="Uses real LLM and exceeds rate limits on collection")
def test_chain_ad_hoc():
    rag = LegalRAG()

    result = rag.ask(
        "What transfer restrictions apply?"
    )

    print("\n=== ANSWER ===\n")
    print(result["answer"])

    print("\n=== SOURCES ===\n")

    for i, citation in enumerate(result["citations"], start=1):
        print(
            f"[{i}] "
            f"{citation['document']} "
            f"— Page {citation['page']} "
            f"— {citation['section']}"
        )