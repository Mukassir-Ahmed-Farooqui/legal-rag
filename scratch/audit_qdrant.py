"""
Full Retrieval & Citation Audit for Legal RAG
=============================================
Queries Qdrant directly — no embedding model needed.
Writes results to scratch/audit_output.txt
"""
import os, sys, json
from collections import Counter, defaultdict

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue

QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
OUT = os.path.join(os.path.dirname(__file__), "audit_output.txt")

COLLECTION_SECTIONS = "legal_sections"
COLLECTION_SENTENCES = "legal_sentences"


def main():
    client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

    with open(OUT, "w", encoding="utf-8") as f:

        # ══════════════════════════════════════════════════════════════
        # 1. COLLECTION INFO
        # ══════════════════════════════════════════════════════════════
        f.write("=" * 80 + "\n")
        f.write("1. COLLECTION INFO\n")
        f.write("=" * 80 + "\n\n")

        for coll_name in [COLLECTION_SECTIONS, COLLECTION_SENTENCES]:
            try:
                info = client.get_collection(coll_name)
                f.write(f"  {coll_name}:\n")
                f.write(f"    points_count: {info.points_count}\n")
                f.write(f"    vectors_count: {info.vectors_count}\n\n")
            except Exception as e:
                f.write(f"  {coll_name}: ERROR - {e}\n\n")

        # ══════════════════════════════════════════════════════════════
        # 2. DATA INTEGRITY AUDIT — scroll all points
        # ══════════════════════════════════════════════════════════════
        f.write("=" * 80 + "\n")
        f.write("2. DATA INTEGRITY AUDIT\n")
        f.write("=" * 80 + "\n\n")

        all_sections = []
        all_sentences = []

        # Scroll sections
        offset = None
        while True:
            points, offset = client.scroll(
                collection_name=COLLECTION_SECTIONS,
                limit=1000,
                with_payload=True,
                offset=offset,
            )
            all_sections.extend(points)
            if offset is None:
                break

        # Scroll sentences
        offset = None
        while True:
            points, offset = client.scroll(
                collection_name=COLLECTION_SENTENCES,
                limit=1000,
                with_payload=True,
                offset=offset,
            )
            all_sentences.extend(points)
            if offset is None:
                break

        f.write(f"  Total section points: {len(all_sections)}\n")
        f.write(f"  Total sentence points: {len(all_sentences)}\n\n")

        # Per-document breakdown
        sec_by_doc = defaultdict(list)
        sent_by_doc = defaultdict(list)

        for p in all_sections:
            doc_id = p.payload.get("doc_id", "MISSING")
            sec_by_doc[doc_id].append(p)

        for p in all_sentences:
            doc_id = p.payload.get("doc_id", "MISSING")
            sent_by_doc[doc_id].append(p)

        all_doc_ids = set(sec_by_doc.keys()) | set(sent_by_doc.keys())

        f.write("  Per-document breakdown:\n")
        f.write(f"  {'doc_id':<80s} {'sections':>8s} {'sentences':>9s} {'filename'}\n")
        f.write("  " + "-" * 120 + "\n")

        for doc_id in sorted(all_doc_ids):
            secs = sec_by_doc.get(doc_id, [])
            sents = sent_by_doc.get(doc_id, [])
            filenames = set()
            for p in secs + sents:
                filenames.add(p.payload.get("filename", "MISSING"))
            f.write(f"  {doc_id:<80s} {len(secs):>8d} {len(sents):>9d} {filenames}\n")

        # Check for orphan sentences (section_id points to non-existent section)
        f.write("\n\n  Orphan sentence check:\n")
        section_chunk_ids = set()
        for p in all_sections:
            section_chunk_ids.add(p.payload.get("chunk_id", ""))

        orphan_count = 0
        for p in all_sentences:
            sid = p.payload.get("section_id", "")
            if sid and sid not in section_chunk_ids:
                orphan_count += 1
                if orphan_count <= 5:
                    f.write(f"    ORPHAN: sentence chunk_id={p.payload.get('chunk_id')} "
                            f"references section_id={sid} (not found in sections)\n")
                    f.write(f"           doc_id={p.payload.get('doc_id')} "
                            f"filename={p.payload.get('filename')}\n")

        f.write(f"  Total orphan sentences: {orphan_count}\n\n")

        # Check for duplicate doc_ids with different filenames
        f.write("  Duplicate / mismatch check:\n")
        doc_filenames = defaultdict(set)
        for p in all_sections + all_sentences:
            doc_filenames[p.payload.get("doc_id", "")].add(p.payload.get("filename", ""))
        for doc_id, fns in doc_filenames.items():
            if len(fns) > 1:
                f.write(f"    WARNING: doc_id={doc_id} has multiple filenames: {fns}\n")
        f.write("  (no output = no mismatches)\n\n")

        # ══════════════════════════════════════════════════════════════
        # 3. HEADING DISTRIBUTION per document
        # ══════════════════════════════════════════════════════════════
        f.write("=" * 80 + "\n")
        f.write("3. HEADING DISTRIBUTION (stored in Qdrant payloads)\n")
        f.write("=" * 80 + "\n\n")

        for doc_id in sorted(all_doc_ids):
            f.write(f"  Document: {doc_id}\n")
            heading_counter = Counter()
            for p in sec_by_doc.get(doc_id, []):
                heading_counter[p.payload.get("heading", "MISSING")] += 1
            f.write("    Section headings:\n")
            for h, c in heading_counter.most_common():
                f.write(f"      {c:3d}x  \"{h}\"\n")

            heading_counter2 = Counter()
            for p in sent_by_doc.get(doc_id, []):
                heading_counter2[p.payload.get("heading", "MISSING")] += 1
            f.write("    Sentence headings:\n")
            for h, c in heading_counter2.most_common():
                f.write(f"      {c:3d}x  \"{h}\"\n")
            f.write("\n")

        # ══════════════════════════════════════════════════════════════
        # 4. SAMPLE PAYLOADS
        # ══════════════════════════════════════════════════════════════
        f.write("=" * 80 + "\n")
        f.write("4. SAMPLE PAYLOADS (first 2 sections & 2 sentences per doc)\n")
        f.write("=" * 80 + "\n\n")

        for doc_id in sorted(all_doc_ids):
            f.write(f"  --- {doc_id} ---\n")
            for i, p in enumerate(sec_by_doc.get(doc_id, [])[:2]):
                payload = dict(p.payload)
                payload["text"] = payload.get("text", "")[:150] + "..."
                f.write(f"  Section {i}: {json.dumps(payload, indent=4, default=str)}\n")
            for i, p in enumerate(sent_by_doc.get(doc_id, [])[:2]):
                payload = dict(p.payload)
                payload["text"] = payload.get("text", "")[:150] + "..."
                f.write(f"  Sentence {i}: {json.dumps(payload, indent=4, default=str)}\n")
            f.write("\n")

        # ══════════════════════════════════════════════════════════════
        # 5. SECTION_ID LINKAGE CHECK
        # ══════════════════════════════════════════════════════════════
        f.write("=" * 80 + "\n")
        f.write("5. SECTION_ID LINKAGE (sentence.section_id → section.chunk_id)\n")
        f.write("=" * 80 + "\n\n")

        # For each sentence, check if its section_id matches a section in the SAME doc
        cross_doc_links = 0
        for p in all_sentences:
            sid = p.payload.get("section_id", "")
            sent_doc = p.payload.get("doc_id", "")
            # Find the section with that chunk_id
            for sp in all_sections:
                if sp.payload.get("chunk_id") == sid:
                    sec_doc = sp.payload.get("doc_id", "")
                    if sec_doc != sent_doc:
                        cross_doc_links += 1
                        if cross_doc_links <= 5:
                            f.write(f"    CROSS-DOC LINK: sentence doc_id={sent_doc} "
                                    f"→ section doc_id={sec_doc} (section_id={sid})\n")
                    break

        f.write(f"  Total cross-doc section_id links: {cross_doc_links}\n\n")

        # ══════════════════════════════════════════════════════════════
        # 6. chunk_id COLLISION CHECK
        # ══════════════════════════════════════════════════════════════
        f.write("=" * 80 + "\n")
        f.write("6. CHUNK_ID / POINT_ID COLLISION CHECK\n")
        f.write("=" * 80 + "\n\n")

        # Check if multiple points share the same point ID (Qdrant ID)
        sec_ids = [p.id for p in all_sections]
        sec_id_counts = Counter(sec_ids)
        sec_collisions = {k: v for k, v in sec_id_counts.items() if v > 1}
        f.write(f"  Section point ID collisions: {len(sec_collisions)}\n")
        for pid, cnt in list(sec_collisions.items())[:5]:
            f.write(f"    point_id={pid} appears {cnt} times\n")
            for p in all_sections:
                if p.id == pid:
                    f.write(f"      doc_id={p.payload.get('doc_id')} "
                            f"chunk_id={p.payload.get('chunk_id')} "
                            f"heading={p.payload.get('heading')}\n")

        sent_ids = [p.id for p in all_sentences]
        sent_id_counts = Counter(sent_ids)
        sent_collisions = {k: v for k, v in sent_id_counts.items() if v > 1}
        f.write(f"  Sentence point ID collisions: {len(sent_collisions)}\n")
        for pid, cnt in list(sent_collisions.items())[:5]:
            f.write(f"    point_id={pid} appears {cnt} times\n")
            for p in all_sentences:
                if p.id == pid:
                    f.write(f"      doc_id={p.payload.get('doc_id')} "
                            f"chunk_id={p.payload.get('chunk_id')} "
                            f"heading={p.payload.get('heading')}\n")

        # Check chunk_id collisions across documents
        f.write("\n  chunk_id collisions across documents:\n")
        chunk_id_to_docs = defaultdict(set)
        for p in all_sections:
            chunk_id_to_docs[p.payload.get("chunk_id", "")].add(p.payload.get("doc_id", ""))
        for p in all_sentences:
            chunk_id_to_docs[p.payload.get("chunk_id", "")].add(p.payload.get("doc_id", ""))

        cross_doc_chunks = {k: v for k, v in chunk_id_to_docs.items() if len(v) > 1}
        f.write(f"  chunk_ids shared across docs: {len(cross_doc_chunks)}\n")
        for cid, docs in list(cross_doc_chunks.items())[:10]:
            f.write(f"    chunk_id={cid} → doc_ids={docs}\n")

        f.write("\n")

    print(f"Audit written to: {OUT}")
    print(f"Sections: {len(all_sections)}, Sentences: {len(all_sentences)}")
    print(f"Documents: {len(all_doc_ids)}")


if __name__ == "__main__":
    main()
