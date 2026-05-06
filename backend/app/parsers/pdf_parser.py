"""
PDF text extraction using pdfplumber.

Public API
----------
extract_text_from_pdf(file_bytes: bytes) -> str
"""

import io
import logging
from typing import Optional

import pdfplumber

logger = logging.getLogger(__name__)


def _table_to_markdown(table: list[list[Optional[str]]]) -> str:
    """
    Convert a pdfplumber table (list-of-rows, each row a list of cell strings)
    to a simple pipe-delimited Markdown table.

    None cells are replaced with an empty string.
    """
    if not table:
        return ""

    rows: list[list[str]] = [
        [cell if cell is not None else "" for cell in row] for row in table
    ]

    # Determine column widths for alignment
    col_count = max(len(row) for row in rows)

    # Pad short rows
    for row in rows:
        while len(row) < col_count:
            row.append("")

    def _fmt_row(row: list[str]) -> str:
        return "| " + " | ".join(cell.replace("\n", " ").strip() for cell in row) + " |"

    lines: list[str] = []
    for idx, row in enumerate(rows):
        lines.append(_fmt_row(row))
        if idx == 0:
            # Separator after header row
            lines.append("| " + " | ".join("---" for _ in range(col_count)) + " |")

    return "\n".join(lines)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract all text from a PDF document.

    Strategy
    --------
    1. For each page, extract plain text via pdfplumber.
    2. For each table found on the page, replace the bounding-box text with a
       Markdown-formatted table so downstream LLMs can parse tabular data.
    3. Pages are joined with a double newline.

    Parameters
    ----------
    file_bytes:
        Raw bytes of the PDF file.

    Returns
    -------
    str
        Extracted text.  Returns an empty string if nothing could be extracted.
    """
    page_texts: list[str] = []

    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            logger.debug("Opened PDF with %d pages", len(pdf.pages))

            for page_num, page in enumerate(pdf.pages, start=1):
                parts: list[str] = []

                # --- Plain text ---------------------------------------------------
                raw_text: Optional[str] = page.extract_text(
                    x_tolerance=3,
                    y_tolerance=3,
                    layout=False,
                )
                if raw_text:
                    parts.append(raw_text.strip())

                # --- Tables -------------------------------------------------------
                try:
                    tables = page.extract_tables(
                        table_settings={
                            "vertical_strategy": "lines",
                            "horizontal_strategy": "lines",
                        }
                    )
                    for tbl in tables:
                        md = _table_to_markdown(tbl)
                        if md:
                            parts.append(md)
                except Exception as tbl_exc:
                    logger.debug(
                        "Table extraction failed on page %d: %s", page_num, tbl_exc
                    )

                if parts:
                    page_texts.append(f"--- Page {page_num} ---\n" + "\n\n".join(parts))

    except Exception as exc:
        logger.error("Failed to extract text from PDF: %s", exc)
        return ""

    return "\n\n".join(page_texts)
