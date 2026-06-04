# src/ingestion/parser.py

import re
import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

from docling.document_converter import DocumentConverter
from docling.datamodel.pipeline_options import PdfPipelineOptions


def clean_heading(text: str) -> str:

    # Strip trailing dash separators (e.g. "Section 1 ----------")
    text = re.sub(r"-{2,}.*$", "", text)

    # Normalise whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()


@dataclass
class DocElement:
    element_type: str
    text: str
    page_num: int
    level: Optional[int] = None
    bbox: Optional[dict] = None
    parent_heading: Optional[str] = None


@dataclass
class ParsedDocument:
    doc_id: str
    filename: str
    source_path: str
    num_pages: int
    elements: list[DocElement] = field(default_factory=list)


def parse_pdf(pdf_path: Path, doc_id: Optional[str] = None) -> ParsedDocument:
    """
    Parse a PDF with Docling, returning structured elements
    (headings, paragraphs, tables) with page numbers and bboxes.
    """
    if not doc_id:
        doc_id = str(uuid.uuid4())

    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = False
    pipeline_options.do_table_structure = True

    converter = DocumentConverter()
    result = converter.convert(str(pdf_path))
    doc = result.document

    elements = []
    current_heading: Optional[str] = None

    for element, _level in doc.iterate_items():

        label = str(getattr(element, "label", "text"))
        text = getattr(element, "text", "").strip()

        if not text:
            continue

        # Promote legal clause titles to headings
        if label == "list_item":

            first_sentence = text.split(".")[0].strip()

            if (
                first_sentence
                and len(first_sentence) < 80
                and first_sentence[0].isupper()
            ):
                label = "heading_1"

        page_num = 1
        bbox = None

        if hasattr(element, "prov") and element.prov:

            prov = element.prov[0]

            page_num = getattr(
                prov,
                "page_no",
                1,
            )

            if hasattr(prov, "bbox"):

                b = prov.bbox

                bbox = {
                    "x0": b.l,
                    "y0": b.t,
                    "x1": b.r,
                    "y1": b.b,
                }

        level = None
        is_heading = "heading" in label.lower() or "section_header" in label.lower()

        if is_heading:

            try:
                level = int(label.split("_")[-1])

            except (ValueError, IndexError):
                level = 1

            text = clean_heading(text)
            current_heading = text

        elements.append(
            DocElement(
                element_type=label,
                text=text,
                page_num=page_num,
                level=level,
                bbox=bbox,
                parent_heading=(
                    current_heading
                    if not is_heading
                    else None
                ),
            )
        )

    return ParsedDocument(
        doc_id=doc_id,
        filename=pdf_path.name,
        source_path=str(pdf_path),
        num_pages=(
            len(doc.pages)
            if hasattr(doc, "pages")
            else 0
        ),
        elements=elements,
    )