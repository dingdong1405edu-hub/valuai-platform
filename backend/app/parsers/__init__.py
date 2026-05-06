"""
Document parser dispatcher.

Public API
----------
parse_document(filename: str, file_bytes: bytes) -> str
    Detect the file extension and delegate to the appropriate parser.
    Returns extracted text as a single string.
"""

import csv
import io
import logging
import os

logger = logging.getLogger(__name__)


async def parse_document(filename: str, file_bytes: bytes) -> str:
    """
    Extract text from a document based on its file extension.

    Supported formats
    -----------------
    - .pdf              → pdfplumber
    - .xlsx / .xls      → openpyxl
    - .docx / .doc      → python-docx
    - .txt              → plain UTF-8 decode
    - .csv              → csv.reader → tab-separated text

    Parameters
    ----------
    filename:
        Original filename (used for extension detection only).
    file_bytes:
        Raw file contents.

    Returns
    -------
    str
        Extracted text.  Empty string if the format is unsupported or parsing
        fails.
    """
    _, ext = os.path.splitext(filename.lower())

    if ext == ".pdf":
        from app.parsers.pdf_parser import extract_text_from_pdf  # noqa: PLC0415
        return extract_text_from_pdf(file_bytes)

    if ext in {".xlsx", ".xls"}:
        from app.parsers.excel_parser import extract_text_from_excel  # noqa: PLC0415
        return extract_text_from_excel(file_bytes)

    if ext in {".docx", ".doc"}:
        from app.parsers.docx_parser import extract_text_from_docx  # noqa: PLC0415
        return extract_text_from_docx(file_bytes)

    if ext == ".txt":
        return _parse_text(file_bytes)

    if ext == ".csv":
        return _parse_csv(file_bytes)

    logger.warning("Unsupported file extension '%s' for file '%s'", ext, filename)
    # Attempt a generic UTF-8 decode as a last resort
    return _parse_text(file_bytes)


# ---------------------------------------------------------------------------
# Inline plain-text helpers (no external dependency)
# ---------------------------------------------------------------------------


def _parse_text(file_bytes: bytes) -> str:
    """Decode bytes to string, trying UTF-8 then latin-1 as fallback."""
    for encoding in ("utf-8", "utf-8-sig", "latin-1", "cp1252"):
        try:
            return file_bytes.decode(encoding).strip()
        except UnicodeDecodeError:
            continue
    # Final fallback: replace un-decodable bytes
    return file_bytes.decode("utf-8", errors="replace").strip()


def _parse_csv(file_bytes: bytes) -> str:
    """
    Parse a CSV file and return tab-separated text where each row is a line.
    Column names are preserved in the first row.
    """
    text = _parse_text(file_bytes)
    lines: list[str] = []
    try:
        reader = csv.reader(io.StringIO(text))
        for row in reader:
            lines.append("\t".join(cell.strip() for cell in row))
    except Exception as exc:
        logger.warning("CSV parsing error: %s — returning raw text", exc)
        return text
    return "\n".join(lines)
