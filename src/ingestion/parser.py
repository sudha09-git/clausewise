from pathlib import Path

import fitz  # PyMuPDF
from docx import Document as DocxDocument


def extract_text_from_pdf(file_path: str) -> str:
    """Extract text from a PDF, preserving page breaks as double newlines."""
    doc = fitz.open(file_path)
    pages = [page.get_text("text") for page in doc]
    doc.close()
    return "\n\n".join(pages)


def extract_text_from_docx(file_path: str) -> str:
    """Extract text from a DOCX, one paragraph per line."""
    doc = DocxDocument(file_path)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def extract_text_from_txt(file_path: str) -> str:
    """Read a plain text file (used for our synthetic sample contracts)."""
    return Path(file_path).read_text(encoding="utf-8")


def extract_text(file_path: str) -> str:
    """Dispatch to the right extractor based on file extension."""
    suffix = Path(file_path).suffix.lower()
    if suffix == ".pdf":
        return extract_text_from_pdf(file_path)
    elif suffix == ".docx":
        return extract_text_from_docx(file_path)
    elif suffix == ".txt":
        return extract_text_from_txt(file_path)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")