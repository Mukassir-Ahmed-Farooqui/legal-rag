import asyncio
import json
from src.retrieval.retriever import HierarchicalRetriever
from src.storage.qdrant_store import get_client, get_embedder

async def run_audit():
    question = "What is the termination date?"
    
    print("--- PHASE 1 & 4: RETRIEVAL AUDIT ---")
    retriever = HierarchicalRetriever(get_client(), get_embedder())
    
    results = retriever.retrieve(question, doc_id=None, query_type="FACT")
    
    print("RAW SECTIONS (Dense Retrieval Top 20):")
    for i, s in enumerate(results.raw_sections):
        print(f"Rank: {i}, ChunkID: {s.chunk_id}, DocID: {s.doc_id}, Page: {s.page_num}, Score: {s.score}, Text: {s.text[:150]}")
        
    print("\nBM25 RESULTS (Sparse Retrieval):")
    if results.bm25_results:
        for i, (idx, score) in enumerate(results.bm25_results):
            s = results.raw_sections[idx]
            print(f"Rank: {i}, ChunkID: {s.chunk_id}, DocID: {s.doc_id}, Page: {s.page_num}, BM25 Score: {score}, Text: {s.text[:150]}")
    else:
        print("No BM25 results")

    print("\nRRF FUSION RESULTS:")
    if results.fused:
        section_lookup = {s.chunk_id: s for s in results.raw_sections}
        for i, (chunk_id, rrf_score) in enumerate(results.fused):
            s = section_lookup[chunk_id]
            print(f"Rank: {i}, ChunkID: {s.chunk_id}, DocID: {s.doc_id}, Page: {s.page_num}, RRF Score: {rrf_score}, Text: {s.text[:150]}")
    else:
        print("No Fusion results")

    print("\nFINAL CONTEXT (Sentences):")
    for i, s in enumerate(results.sentences):
        print(f"Rank: {i}, ChunkID: {s.chunk_id}, DocID: {s.doc_id}, Page: {s.page_num}, Score: {s.score}, Text: {s.text[:150]}")

if __name__ == "__main__":
    asyncio.run(run_audit())
