from src.workflows.legal_graph import legal_graph, retrieve_node, generate_node, citation_node, LegalState
from src.retrieval.retriever import Chunk
from unittest.mock import MagicMock

def test_graph_compilation():
    assert legal_graph is not None
    # We can verify nodes exist in the graph
    node_names = set(legal_graph.nodes.keys())
    assert "retrieve" in node_names
    assert "generate" in node_names
    assert "citations" in node_names
    print("test_graph_compilation passed!")

def test_retrieve_node_empty():
    state: LegalState = {"question": ""}
    res = retrieve_node(state)
    assert res == {"retrieved_chunks": []}
    print("test_retrieve_node_empty passed!")

def test_citation_node_empty():
    state: LegalState = {"retrieved_chunks": []}
    res = citation_node(state)
    assert res == {"citations": []}
    print("test_citation_node_empty passed!")

def test_citation_node_with_chunks():
    chunk1 = Chunk(
        chunk_id="1",
        chunk_type="sentence",
        text="This is a test.",
        heading="Section 1",
        page_num=2,
        doc_id="doc_123",
        filename="contract.pdf"
    )
    chunk2 = Chunk(
        chunk_id="2",
        chunk_type="sentence",
        text="This is another test.",
        heading="Section 1",
        page_num=2,
        doc_id="doc_123",
        filename="contract.pdf"
    )
    chunk3 = Chunk(
        chunk_id="3",
        chunk_type="sentence",
        text="Different section.",
        heading="Section 2",
        page_num=3,
        doc_id="doc_123",
        filename="contract.pdf"
    )
    
    state: LegalState = {"retrieved_chunks": [chunk1, chunk2, chunk3]}
    res = citation_node(state)
    citations = res["citations"]
    
    # Check that duplicates (same page and heading) are removed
    assert len(citations) == 2
    assert citations[0] == {"document": "contract.pdf", "page": 2, "section": "Section 1"}
    assert citations[1] == {"document": "contract.pdf", "page": 3, "section": "Section 2"}
    print("test_citation_node_with_chunks passed!")

def test_generate_node_mock(monkeypatch=None):
    # Mock the generate function to avoid hitting Groq API
    import src.workflows.legal_graph
    original_generate = src.workflows.legal_graph.generate
    src.workflows.legal_graph.generate = lambda prompt: "Mocked Answer"
    
    try:
        chunk = Chunk(
            chunk_id="1",
            chunk_type="sentence",
            text="This is test text.",
            heading="Section 1",
            page_num=1,
            doc_id="doc_123",
            filename="contract.pdf"
        )
        state: LegalState = {
            "question": "What is the test?",
            "retrieved_chunks": [chunk]
        }
        
        res = generate_node(state)
        assert res == {"answer": "Mocked Answer"}
        print("test_generate_node_mock passed!")
    finally:
        src.workflows.legal_graph.generate = original_generate

if __name__ == "__main__":
    print("Running graph unit tests...")
    test_graph_compilation()
    test_retrieve_node_empty()
    test_citation_node_empty()
    test_citation_node_with_chunks()
    test_generate_node_mock()
    print("All graph unit tests passed successfully!")
