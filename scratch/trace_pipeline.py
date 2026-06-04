"""
Full pipeline trace: PDF → parsed elements → section chunks → stored headings.
Writes results to scratch/trace_output.txt (UTF-8).
"""
import os, sys

# Ensure project root is on path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from pathlib import Path
from src.ingestion.parser import parse_pdf
from src.ingestion.chunker import chunk_document

PDF_PATH = Path("data/uploads/ArcaUsTreasuryFund_20200207_N-2_EX-99.K5_11971930_EX-99.K5_Development Agreement.pdf")
OUT_PATH = Path(os.path.dirname(__file__)) / "trace_output.txt"


def main():
    if not PDF_PATH.exists():
        print(f"PDF not found: {PDF_PATH}")
        sys.exit(1)

    parsed = parse_pdf(PDF_PATH)

    with open(OUT_PATH, "w", encoding="utf-8") as f:

        # ── STAGE 1: Raw parsed elements ──────────────────────────────
        f.write("=" * 80 + "\n")
        f.write("STAGE 1: RAW PARSED ELEMENTS (from Docling via parser.py)\n")
        f.write(f"Total elements: {len(parsed.elements)}\n")
        f.write("=" * 80 + "\n\n")

        heading_count = 0
        for i, el in enumerate(parsed.elements):
            is_heading = "heading" in el.element_type.lower() or "section_header" in el.element_type.lower()
            if is_heading:
                heading_count += 1
            marker = ">>> HEADING <<<" if is_heading else ""
            f.write(f"[{i:03d}] type={el.element_type:15s} page={el.page_num:2d} {marker}\n")
            f.write(f"      text: {el.text[:200]}\n")
            if el.parent_heading:
                f.write(f"      parent_heading: {el.parent_heading}\n")
            f.write("\n")

        f.write(f"\nTotal headings detected by parser: {heading_count}\n\n")

        # ── STAGE 2: Section chunks from chunker ──────────────────────
        section_chunks, sentence_chunks = chunk_document(
            parsed.elements,
            doc_id=parsed.doc_id,
            filename=parsed.filename,
        )

        f.write("=" * 80 + "\n")
        f.write("STAGE 2: SECTION CHUNKS (from chunker.py)\n")
        f.write(f"Total section chunks: {len(section_chunks)}\n")
        f.write(f"Total sentence chunks: {len(sentence_chunks)}\n")
        f.write("=" * 80 + "\n\n")

        for i, sc in enumerate(section_chunks):
            f.write(f"--- Section Chunk {i} ---\n")
            f.write(f"  heading   : {sc.heading}\n")
            f.write(f"  chunk_id  : {sc.chunk_id}\n")
            f.write(f"  page      : {sc.page_num}-{sc.end_page_num}\n")
            f.write(f"  tokens    : {sc.token_count}\n")
            f.write(f"  text[0:300]: {sc.text[:300]}\n")
            f.write("\n")

        # ── STAGE 3: Heading distribution summary ─────────────────────
        f.write("=" * 80 + "\n")
        f.write("STAGE 3: HEADING DISTRIBUTION SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        from collections import Counter
        heading_dist = Counter(sc.heading for sc in section_chunks)
        for h, count in heading_dist.most_common():
            f.write(f"  {count:3d}x  \"{h}\"\n")

        f.write("\n\n")

        # same for sentence chunks
        sent_heading_dist = Counter(sc.heading for sc in sentence_chunks)
        f.write("Sentence chunk heading distribution:\n")
        for h, count in sent_heading_dist.most_common():
            f.write(f"  {count:3d}x  \"{h}\"\n")

    print(f"Trace written to: {OUT_PATH}")
    print(f"Elements: {len(parsed.elements)}, Headings: {heading_count}")
    print(f"Section chunks: {len(section_chunks)}, Sentence chunks: {len(sentence_chunks)}")


if __name__ == "__main__":
    main()
