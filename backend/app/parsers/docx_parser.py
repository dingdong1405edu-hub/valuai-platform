"""
DOCX text extraction using python-docx.

Public API
----------
extract_text_from_docx(file_bytes: bytes) -> str
"""

import io
import logging
from typing import Optional

from docx import Document as DocxDocument
from docx.oxml.ns import qn
from docx.table import Table
from docx.text.paragraph import Paragraph

logger = logging.getLogger(__name__)


def _table_to_text(table: Table) -> str:
    """
    Convert a python-docx Table to a pipe-delimited Markdown-style table.
    """
    lines: list[str] = []

    for row_idx, row in enumerate(table.rows):
        cells = [cell.text.replace("\n", " ").strip() for cell in row.cells]
        lines.append("| " + " | ".join(cells) + " |")
        if row_idx == 0:
            col_count = len(cells)
            lines.append("| " + " | ".join(["---"] * col_count) + " |")

    return "\n".join(lines)


def _paragraph_text(para: Paragraph) -> str:
    """Return the full text of a paragraph, preserving bold/italic markers if useful."""
    return para.text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract all text from a DOCX document.

    Extraction order
    ----------------
    The function iterates over the document body's child elements in document
    order so that paragraphs and tables appear in the correct sequence.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the DOCX file.

    Returns
    -------
    str
        Extracted text, or empty string on failure.
    """
    try:
        doc = DocxDocument(io.BytesIO(file_bytes))
    except Exception as exc:
        logger.error("Failed to open DOCX document: %s", exc)
        return ""

    parts: list[str] = []

    try:
        # Walk body children in document order to preserve paragraph/table interleaving
        body = doc.element.body
        for child in body:
            tag = child.tag

            if tag == qn("w:p"):
                # Paragraph
                para = Paragraph(child, doc)
                text = _paragraph_text(para)
                if text:
                    # Preserve heading level if detectable
                    style_name = para.style.name if para.style else ""
                    if style_name.startswith("Heading"):
                        level = style_name.replace("Heading", "").strip()
                        prefix = "#" * int(level) if level.isdigit() else "#"
                        parts.append(f"{prefix} {text}")
                    else:
                        parts.append(text)

            elif tag == qn("w:tbl"):
                # Table
                table = Table(child, doc)
                tbl_text = _table_to_text(table)
                if tbl_text:
                    parts.append(tbl_text)

        # Also capture text boxes / shapes in the drawing layer (best-effort)
        for shape in doc.inline_shapes:
            try:
                # Text frames inside inline shapes
                txBx = shape._inline.graphic.graphicData.find(
                    ".//{http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing}txbxContent"
                )
                if txBx is not None:
                    for p in txBx.iter(qn("w:p")):
                        para = Paragraph(p, doc)
                        text = _paragraph_text(para)
                        if text:
                            parts.append(text)
            except Exception:
                pass

    except Exception as exc:
        logger.error("Error while extracting DOCX content: %s", exc)
        return "\n\n".join(parts)  # return whatever we have so far

    return "\n\n".join(parts)
