import re
from typing import TypedDict, Optional, Any
from langgraph.graph import StateGraph, START, END
from src.security.guards import contains_prompt_injection
from src.llm.groq_client import generate
from src.prompts.legal_qa import LEGAL_QA_PROMPT
from src.retrieval.retriever import HierarchicalRetriever
from src.storage.qdrant_store import (
    get_client,
    get_embedder,
)

class LegalState(TypedDict, total=False):
    question: str
    selected_doc_ids: Optional[list[str]]
    retrieved_chunks: list[Any]
    answer: str
    citations: list[dict]
    chat_history: Optional[str]
    retrieval_metadata: Optional[Any]
    formatted_context: Optional[str]
    query_type: Optional[str]
    model_used: Optional[str]

# Retriever will be initialized lazily to avoid PyTorch access violations on startup
_retriever = None

def get_retriever():
    global _retriever
    if _retriever is None:
        _retriever = HierarchicalRetriever(
            get_client(),
            get_embedder(),
        )
    return _retriever

SUMMARY_PATTERNS = [
    "summar",
    "overview",
    "what is this",
    "what is the document",
    "about this",
    "give me a",
    "provide a",
    "tell me about"
]

COMPARE_PATTERNS = [
    "compare",
    "difference between",
    "vs",
    "versus"
]

def classify_query(question: str) -> str:
    q = question.lower()

    if any(p in q for p in COMPARE_PATTERNS):
        return "COMPARE"

    if any(p in q for p in SUMMARY_PATTERNS):
        return "SUMMARY"

    return "FACT"


def _build_prompt_template(query_type: str) -> str:
    """Select or augment the base prompt based on query type."""
    from src.prompts.legal_qa import LEGAL_QA_PROMPT, LEGAL_COMPARE_PROMPT
    if query_type == "COMPARE":
        return LEGAL_COMPARE_PROMPT
    return LEGAL_QA_PROMPT


def retrieve_node(state: LegalState) -> LegalState:
    question = state.get("question", "")
    selected_doc_ids = state.get("selected_doc_ids", None)

    if not question:
        return {"retrieved_chunks": [], "retrieval_metadata": {}, "query_type": "FACT"}

    query_type = classify_query(question)
    retriever = get_retriever()
    results = retriever.retrieve(question, doc_id=selected_doc_ids, query_type=query_type)

    safe_chunks = []
    for chunk in results.sentences:
        if contains_prompt_injection(chunk.text):
            continue
        safe_chunks.append(chunk)

    metadata = {
        "raw_sections": results.raw_sections,
        "bm25_results": results.bm25_results,
        "fused": results.fused,
        "sections": results.sections,
        "sentences": results.sentences,
        "retrieved_pages": results.sections and sorted(list(set(s.page_num for s in results.sections))) or [],
        "coverage_pct": getattr(results, "coverage_pct", 0.0),
        "section_coverage": getattr(results, "section_coverage", ""),
        "rewritten_query": getattr(results, "rewritten_query", None),
    }

    return {"retrieved_chunks": safe_chunks, "retrieval_metadata": metadata, "query_type": query_type}


def generate_node(state: LegalState) -> LegalState:
    question = state.get("question", "")
    retrieved_chunks = state.get("retrieved_chunks", [])
    retrieved_chunks = sorted(retrieved_chunks, key=lambda c: getattr(c, 'score', 0.0), reverse=True)
    chat_history = state.get("chat_history", None) or "No previous conversation history."
    query_type = state.get("query_type", "FACT")

    context_parts = []

    for idx, chunk in enumerate(retrieved_chunks):
        citation_id = idx + 1

        context_parts.append(
            f"Source [{citation_id}]\n"
            f"Document: {chunk.filename}\n"
            f"Section: {chunk.heading}\n"
            f"Page: {chunk.page_num}\n\n"
            f"{chunk.text}"
        )

    context = "\n\n".join(context_parts)

    prompt_template = _build_prompt_template(query_type)
    prompt = prompt_template.format(
        chat_history=chat_history,
        context=context,
        question=question,
    )

    result = generate(prompt)
    return {"answer": result["text"], "formatted_context": context, "model_used": result["model"]}


def citation_node(state: LegalState) -> LegalState:
    answer = state.get("answer", "")
    if answer.strip() == "I could not find sufficient evidence in the provided documents.":
        return {"citations": []}

    retrieved_chunks = state.get("retrieved_chunks", [])

    if not retrieved_chunks:
        return {"citations": []}

    retrieved_chunks = sorted(retrieved_chunks, key=lambda c: getattr(c, 'score', 0.0), reverse=True)

    # Parse which citation IDs [1], [2], [N] are actually referenced in the answer
    cited_ids = set()
    for match in re.finditer(r'\[(\d+)\]', answer):
        cited_ids.add(int(match.group(1)))

    def _build_citation(chunk):
        preview = chunk.text.strip()
        if len(preview) > 200:
            preview = preview[:200] + "..."
        return {
            "document": chunk.filename,
            "page": chunk.page_num,
            "section": chunk.heading,
            "chunk_id": getattr(chunk, 'chunk_id', ""),
            "score": getattr(chunk, 'score', 0.0),
            "preview": preview
        }

    citations = []
    seen = set()

    for idx, chunk in enumerate(retrieved_chunks):
        citation_number = idx + 1

        # Only include this chunk if the answer actually cites it
        if cited_ids and citation_number not in cited_ids:
            continue

        key = getattr(chunk, 'chunk_id', None)
        if not key:
            key = (chunk.page_num, chunk.heading, chunk.text[:50])

        if key in seen:
            continue

        seen.add(key)
        citations.append(_build_citation(chunk))

    # Fallback: if the answer has no [N] citations at all (LLM ignored the instruction),
    # return all retrieved chunks so the user still gets evidence
    if not citations:
        for chunk in retrieved_chunks:
            key = getattr(chunk, 'chunk_id', None)
            if not key:
                key = (chunk.page_num, chunk.heading, chunk.text[:50])

            if key in seen:
                continue

            seen.add(key)
            citations.append(_build_citation(chunk))

    return {"citations": citations}


builder = StateGraph(LegalState)
builder.add_node("retrieve", retrieve_node)
builder.add_node("generate", generate_node)
builder.add_node("citations", citation_node)

builder.add_edge(START, "retrieve")
builder.add_edge("retrieve", "generate")
builder.add_edge("generate", "citations")
builder.add_edge("citations", END)

legal_graph = builder.compile()
