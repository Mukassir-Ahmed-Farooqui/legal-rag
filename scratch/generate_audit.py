import asyncio
import json
from src.retrieval.retriever import HierarchicalRetriever
from src.storage.qdrant_store import get_client, get_embedder, COLLECTION_SECTIONS, COLLECTION_SENTENCES
from qdrant_client.models import Filter, FieldCondition

async def run_audit():
    question = "What is the termination date?"
    doc_id = "3b01e57f-2ae6-42ca-9436-9cb1e852ec82" # PelicanDelivers
    
    with open("C:/Users/Mukashifa Fatima/.gemini/antigravity-ide/brain/3d447f36-a936-4848-aaa0-b5ce81e6d433/audit_report.md", "w") as f:
        f.write("# Retrieval Pipeline Audit\n\n")
        f.write("## Phase 1 & 4: Retrieval Flow & Quality Audit\n")
        f.write("Query: 'What is the termination date?'\n\n")
        
        retriever = HierarchicalRetriever(get_client(), get_embedder())
        results = retriever.retrieve(question, doc_id=doc_id, query_type="FACT")
        
        f.write("### 1. Raw Vector Retrieval Results (Top 20)\n")
        for i, s in enumerate(results.raw_sections):
            f.write(f"- **Rank {i}**: Score: `{s.score}`, Page: `{s.page_num}`, Heading: `{s.heading}`\n")
            f.write(f"  - Preview: `{s.text[:150]}`\n")
            
        f.write("\n### 2. Raw BM25 Retrieval Results\n")
        if results.bm25_results:
            for i, (idx, score) in enumerate(results.bm25_results):
                s = results.raw_sections[idx]
                f.write(f"- **Rank {i}**: BM25 Score: `{score}`, Page: `{s.page_num}`, Heading: `{s.heading}`\n")
                f.write(f"  - Preview: `{s.text[:150]}`\n")
        else:
            f.write("No BM25 results\n")

        f.write("\n### 3. RRF Fusion Output\n")
        if results.fused:
            section_lookup = {s.chunk_id: s for s in results.raw_sections}
            for i, (chunk_id, rrf_score) in enumerate(results.fused):
                s = section_lookup[chunk_id]
                f.write(f"- **Rank {i}**: RRF Score: `{rrf_score}`, Page: `{s.page_num}`, Heading: `{s.heading}`\n")
                f.write(f"  - Preview: `{s.text[:150]}`\n")
        
        f.write("\n### 4. Final Context Passed to LLM (Sentences)\n")
        for i, s in enumerate(results.sentences):
            f.write(f"- **Rank {i}**: Score: `{s.score}`, Page: `{s.page_num}`, Heading: `{s.heading}`\n")
            f.write(f"  - Preview: `{s.text[:150]}`\n")
            
        f.write("\n## Phase 2: Citation Audit\n")
        f.write("- Citations are created in `citation_node` of `legal_graph.py`.\n")
        f.write("- They iterate over `retrieved_chunks` (sentences) and deduplicate by `(page_num, heading)`.\n")
        f.write("- The heading 'Document Summary' comes from `chunker.py` setting `heading = 'Preamble'` or 'Document Summary' for chunks before the first heading.\n")
        
        f.write("\n## Phase 3: Chunking Audit\n")
        client = get_client()
        f.write(f"\nInspecting chunks for doc_id {doc_id}...\n")
        
        sec_hits = client.scroll(
            collection_name=COLLECTION_SECTIONS,
            scroll_filter=Filter(must=[FieldCondition(key="doc_id", match={"value": doc_id})]),
            limit=20,
            with_payload=True
        )[0]
        
        f.write("### Sample Section Chunks\n")
        for hit in sec_hits[:5]:
            p = hit.payload
            f.write(f"- **ChunkID**: `{p['chunk_id']}`, Page: `{p.get('page_num')}`, Heading: `{p.get('heading')}`\n")
            f.write(f"  - Text: `{p['text'][:150]}`\n")

if __name__ == "__main__":
    asyncio.run(run_audit())
